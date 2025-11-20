// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  CssBaseline,
  Box,
  TextField,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  FormControlLabel,
  Tooltip,
  IconButton,
  Tabs,
  Tab,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Fab,
} from '@mui/material';
import {
  ArrowUpward,
  ArrowDownward,
  Close,
  Info,
  Add,
  Edit,
  Delete,
} from '@mui/icons-material';

import MapComponent from './components/MapComponent'; // still used in SearchTab.jsx
import ExploreTab from './components/ExploreTab';
import TagManagerTab from './components/TagManagerTab';
import SearchTab from './components/SearchTab';

function App() {
  const [location, setLocation] = useState({ city: '', country: '' });
  const [position, setPosition] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [locationList, setLocationList] = useState([]);
  const [sortBy, setSortBy] = useState('city');
  const [sortOrder, setSortOrder] = useState('asc');
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [options, setOptions] = useState([]);
  const [descriptions, setDescriptions] = useState({});
  const [currentTab, setCurrentTab] = useState(0);
  const [tags, setTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [entities, setEntities] = useState([]);
  const [newTagName, setNewTagName] = useState('');
  const [newTagDescription, setNewTagDescription] = useState('');
  const [editTag, setEditTag] = useState(null);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [deleteTag, setDeleteTag] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState({
    open: false,
    title: '',
    message: '',
    action: null,
  });

  useEffect(() => {
    fetch('/entity-types')
      .then((res) => res.json())
      .then((data) => {
        setOptions(data.types);
        setDescriptions(data.descriptions);
        setSelectedOptions(data.types);
      })
      .catch((err) =>
        console.error('Error loading entity types:', err),
      );
  }, []);

  useEffect(() => {
    fetch('/api/tags/')
      .then((res) => res.json())
      .then((data) => {
        setTags(data);
        setSelectedTags(data.map(tag => tag.name)); // Select all tags by default
      })
      .catch((err) => console.error('Error loading tags:', err));
  }, []);

  useEffect(() => {
    fetch('/api/entities/')
      .then((res) => res.json())
      .then((data) => {
        setEntities(data);
      })
      .catch((err) => console.error('Error loading entities:', err));
  }, []);

  const handleSearch = () => {
    if (!searchQuery) return;

    // Geocoding using Nominatim API
    fetch(
      `https://nominatim.openstreetmap.org/search?q=${searchQuery}&format=json&limit=1`,
    )
      .then((res) => res.json())
      .then((data) => {
        if (data.length > 0) {
          const { lat, lon, display_name } = data[0];
          const newPosition = {
            lat: parseFloat(lat),
            lng: parseFloat(lon),
          };
          setPosition(newPosition);

          // A simple way to parse city and country from display_name
          const parts = display_name.split(', ');
          const country = parts[parts.length - 1];
          const city = parts[0];

          setLocation({
            city: city || 'N/A',
            country: country || 'N/A',
          });
        } else {
          alert('Location not found');
        }
      })
      .catch((err) => {
        console.error('Error fetching geocoding data:', err);
        alert('Error finding location');
      });
  };

  const handleAddToList = () => {
    if (
      location.city &&
      location.country &&
      location.city !== 'N/A' &&
      location.country !== 'N/A'
    ) {
      const isDuplicate = locationList.some(
        (loc) =>
          loc.city === location.city &&
          loc.country === location.country,
      );
      if (isDuplicate) {
        alert('This place is already in the list');
      } else {
        setLocationList([...locationList, { ...location }]);
      }
    }
  };

  const handleExport = () => {
    const exportList = [...locationList].sort((a, b) =>
      a.city.localeCompare(b.city),
    );
    const tuples = exportList.map((loc) => [loc.city, loc.country]);
    fetch('/export-list', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tuples),
    })
      .then((response) => response.json())
      .then((data) => alert(data.message))
      .catch((error) => console.error('Error:', error));
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const sortedLocationList = [...locationList].sort((a, b) => {
    const primaryA = a[sortBy].toLowerCase();
    const primaryB = b[sortBy].toLowerCase();
    const secondaryA = a[sortBy === 'city' ? 'country' : 'city'].toLowerCase();
    const secondaryB = b[sortBy === 'city' ? 'country' : 'city'].toLowerCase();

    if (primaryA !== primaryB) {
      if (sortOrder === 'asc') {
        return primaryA.localeCompare(primaryB);
      } else {
        return primaryB.localeCompare(primaryA);
      }
    } else {
      // Secondary sort always ascending
      return secondaryA.localeCompare(secondaryB);
    }
  });

  const handleAddTag = () => {
    if (!newTagName.trim()) return;
    fetch('/api/tags/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newTagName,
        description: newTagDescription,
      }),
    })
      .then((res) => res.json())
      .then((newTag) => {
        setTags([...tags, newTag]);
        setNewTagName('');
        setNewTagDescription('');
      })
      .catch((err) => console.error('Error adding tag:', err));
  };

  const handleEditTag = () => {
    if (!editName.trim() || !editTag) return;
    fetch(`/api/tags/${editTag.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: editName,
        description: editDescription,
      }),
    })
      .then((res) => res.json())
      .then((updatedTag) => {
        setTags(
          tags.map((t) =>
            t.id === editTag.id ? updatedTag : t,
          ),
        );
        setEditTag(null);
        setEditName('');
        setEditDescription('');
      })
      .catch((err) => console.error('Error editing tag:', err));
  };

  const handleDeleteTag = () => {
    if (!deleteTag) return;
    fetch(`/api/tags/${deleteTag.id}`, {
      method: 'DELETE',
    })
      .then(() => {
        setTags(tags.filter((t) => t.id !== deleteTag.id));
        setDeleteTag(null);
      })
      .catch((err) => console.error('Error deleting tag:', err));
  };

  const openEditDialog = (tag) => {
    setEditTag(tag);
    setEditName(tag.name);
    setEditDescription(tag.description || '');
  };

  const openDeleteDialog = (tag) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Tag',
      message: `Are you sure you want to delete the tag "${tag.name}"? This will also remove all associations with entities.`,
      action: () => handleDeleteTag(),
    });
    setDeleteTag(tag);
  };

  // Calculate entity count for each tag
  const getTagEntityCount = (tagId) => {
    return entities.filter(entity => 
      entity.tags && entity.tags.some(tag => tag.id === tagId)
    ).length;
  };

  return (
    <>
      <CssBaseline />
      <Tabs
        value={currentTab}
        onChange={(e, newValue) => setCurrentTab(newValue)}
      >
        <Tab label="Search new options" />
        <Tab label="Explore saved options" />
        <Tab label="Tag manager" />
      </Tabs>
      <Container>
        {currentTab === 0 ? (
          <SearchTab
            location={location}
            position={position}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            handleSearch={handleSearch}
            options={options}
            descriptions={descriptions}
            selectedOptions={selectedOptions}
            setSelectedOptions={setSelectedOptions}
            tags={tags}
            selectedTags={selectedTags}
            setSelectedTags={setSelectedTags}
            handleAddToList={handleAddToList}
            handleExport={handleExport}
            locationList={locationList}
            setLocationList={setLocationList}
            sortBy={sortBy}
            sortOrder={sortOrder}
            handleSort={handleSort}
            sortedLocationList={sortedLocationList}
            // 👇 these two are new
            setLocation={setLocation}
            setPosition={setPosition}
          />
        ) : currentTab === 1 ? (
          <ExploreTab
            selectedOptions={selectedOptions}
            locationList={locationList}
          />
        ) : currentTab === 2 ? (
          <TagManagerTab
            newTagName={newTagName}
            setNewTagName={setNewTagName}
            newTagDescription={newTagDescription}
            setNewTagDescription={setNewTagDescription}
            handleAddTag={handleAddTag}
            tags={tags}
            getTagEntityCount={getTagEntityCount}
            openEditDialog={openEditDialog}
            openDeleteDialog={openDeleteDialog}
          />
        ) : null}
      </Container>

      {/* Edit Dialog */}
      <Dialog open={!!editTag} onClose={() => setEditTag(null)}>
        <DialogTitle>Edit Tag</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Warning: Editing this tag will update it for all
            associated entities. This action cannot be undone.
          </DialogContentText>
          <TextField
            label="Tag Name"
            variant="outlined"
            fullWidth
            sx={{ mt: 2 }}
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
          />
          <TextField
            label="Description (optional)"
            variant="outlined"
            fullWidth
            sx={{ mt: 2 }}
            value={editDescription}
            onChange={(e) =>
              setEditDescription(e.target.value)
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditTag(null)}>Cancel</Button>
          <Button
            onClick={handleEditTag}
            variant="contained"
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirm Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={() =>
          setConfirmDialog({ ...confirmDialog, open: false })
        }
      >
        <DialogTitle>{confirmDialog.title}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {confirmDialog.message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() =>
              setConfirmDialog({
                ...confirmDialog,
                open: false,
              })
            }
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              confirmDialog.action &&
                confirmDialog.action();
              setConfirmDialog({
                ...confirmDialog,
                open: false,
              });
            }}
            variant="contained"
            color="error"
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default App;

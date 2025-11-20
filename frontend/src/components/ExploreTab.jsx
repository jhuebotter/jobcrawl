import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  TextField,
  Autocomplete,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  TableSortLabel,
} from '@mui/material';
import { Refresh, Add, Star, StarBorder, Edit, Delete } from '@mui/icons-material';

function ExploreTab({ selectedOptions, locationList }) {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    type: [],
    city: [],
    country: [],
    tag: [],
    starred: false,
  });
  const [filterOptions, setFilterOptions] = useState({
    types: [],
    tags: [],
    cities: [],
    countries: [],
  });
  const [entityTypes, setEntityTypes] = useState([]);
  const [validEntityTypes, setValidEntityTypes] = useState([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [addTagDialog, setAddTagDialog] = useState({ open: false, entity: null });
  const [removeTagDialog, setRemoveTagDialog] = useState({ open: false, entity: null, tag: null });
  const [editDialog, setEditDialog] = useState({ open: false, entity: null });
  const [deleteDialog, setDeleteDialog] = useState({ open: false, entity: null });
  const [editFormData, setEditFormData] = useState({
    name: '',
    type: '',
    city: '',
    country: '',
    description: '',
  });
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'asc' });

  // Update edit form data when dialog opens
  React.useEffect(() => {
    if (editDialog.entity) {
      setEditFormData({
        name: editDialog.entity.name || '',
        type: editDialog.entity.type || '',
        city: editDialog.entity.city || '',
        country: editDialog.entity.country || '',
        description: editDialog.entity.description || '',
      });
    }
  }, [editDialog.entity]);

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch('/api/filters');
      if (!response.ok) {
        throw new Error(`Failed to fetch filter options: ${response.status}`);
      }
      const data = await response.json();
      setFilterOptions(data);
    } catch (err) {
      console.error('Error fetching filter options:', err);
      // Fallback to deriving from entities if API fails
      setFilterOptions({
        types: getUniqueValues('type'),
        tags: getUniqueValues('tags'),
        cities: getUniqueValues('city'),
        countries: getUniqueValues('country'),
      });
    } finally {
      setOptionsLoading(false);
    }
  };

  const fetchEntityTypes = async () => {
    try {
      const response = await fetch('/api/entity-types');
      if (!response.ok) {
        throw new Error(`Failed to fetch entity types: ${response.status}`);
      }
      const data = await response.json();
      setEntityTypes(data.types || []);
    } catch (err) {
      console.error('Error fetching entity types:', err);
      setEntityTypes([]);
    }
  };

  const fetchValidEntityTypes = async () => {
    try {
      const response = await fetch('/entity-types');
      if (!response.ok) {
        throw new Error(`Failed to fetch entity types: ${response.status}`);
      }
      const data = await response.json();
      setValidEntityTypes(data.types);
    } catch (err) {
      console.error('Error fetching entity types:', err);
      // Fallback to hardcoded list
      setValidEntityTypes(['Company', 'NGO', 'University', 'Research Lab', 'Institute', 'Governmental Organization']);
    }
  };

  const fetchEntities = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const queryParams = new URLSearchParams();
      
      // Handle multiple types
      if (filters.type && filters.type.length > 0) {
        filters.type.forEach(type => queryParams.append('type', type));
      }
      
      // Handle multiple cities
      if (filters.city && filters.city.length > 0) {
        filters.city.forEach(city => queryParams.append('city', city));
      }
      
      // Handle multiple countries
      if (filters.country && filters.country.length > 0) {
        filters.country.forEach(country => queryParams.append('country', country));
      }
      
      // Handle multiple tags
      if (filters.tag && filters.tag.length > 0) {
        filters.tag.forEach(tag => queryParams.append('tag', tag));
      }
      
      // Handle starred filter
      if (filters.starred) {
        queryParams.append('starred', 'true');
      }
      
      const response = await fetch(`/api/entities/?${queryParams}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch entities: ${response.status}`);
      }
      const data = await response.json();
      setEntities(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching entities:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFilterOptions();
    fetchValidEntityTypes();
    fetchEntities();
  }, []);

  useEffect(() => {
    fetchEntities();
  }, [filters]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const clearFilters = () => {
    setFilters({
      type: [],
      city: [],
      country: [],
      tag: [],
      starred: false,
    });
  };

  const getUniqueValues = (field) => {
    // Use pre-fetched filter options instead of deriving from current entities
    switch (field) {
      case 'type':
        return filterOptions.types || [];
      case 'tags':
        return filterOptions.tags || [];
      case 'city':
        return filterOptions.cities || [];
      case 'country':
        return filterOptions.countries || [];
      default:
        return [];
    }
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedEntities = React.useMemo(() => {
    let sortableItems = [...entities];
    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        const aValue = a[sortConfig.key] || '';
        const bValue = b[sortConfig.key] || '';
        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [entities, sortConfig]);

  const handleEditEntity = async (entityId, updateData) => {
    try {
      const response = await fetch(`/api/entities/${entityId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      if (!response.ok) {
        throw new Error(`Failed to update entity: ${response.status}`);
      }
      await fetchEntities(); // Refresh data
      await fetchFilterOptions(); // Refresh filter options in case new values were added
    } catch (err) {
      console.error('Error updating entity:', err);
      setError('Failed to update entity');
    }
  };

  const handleDeleteEntity = async (entityId) => {
    try {
      const response = await fetch(`/api/entities/${entityId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`Failed to delete entity: ${response.status}`);
      }
      await fetchEntities(); // Refresh data
      await fetchFilterOptions(); // Refresh filter options
    } catch (err) {
      console.error('Error deleting entity:', err);
      setError('Failed to delete entity');
    }
  };

  const handleAddTag = async (entityId, tagName) => {
    try {
      const response = await fetch(`/api/entities/${entityId}/tags/${encodeURIComponent(tagName)}`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to add tag: ${response.status}`);
      }
      await fetchEntities(); // Refresh data
      await fetchFilterOptions(); // Refresh filter options in case new tag was added
    } catch (err) {
      console.error('Error adding tag:', err);
      setError('Failed to add tag');
    }
  };

  const handleRemoveTag = async (entityId, tagName) => {
    try {
      const response = await fetch(`/api/entities/${entityId}/tags/${encodeURIComponent(tagName)}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`Failed to remove tag: ${response.status}`);
      }
      await fetchEntities(); // Refresh data
      await fetchFilterOptions(); // Refresh filter options
    } catch (err) {
      console.error('Error removing tag:', err);
      setError('Failed to remove tag');
    }
  };

  const handleToggleStar = async (entityId, currentlyStarred) => {
    try {
      const response = await fetch(`/api/entities/${entityId}/star`, {
        method: currentlyStarred ? 'DELETE' : 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to ${currentlyStarred ? 'unstar' : 'star'} entity: ${response.status}`);
      }
      await fetchEntities(); // Refresh data
    } catch (err) {
      console.error(`Error ${currentlyStarred ? 'unstarring' : 'starring'} entity:`, err);
      setError(`Failed to ${currentlyStarred ? 'unstar' : 'star'} entity`);
    }
  };

  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Explore Database Entities
      </Typography>
      <Typography variant="body1" paragraph>
        Browse all organizations and entities stored in the database.
      </Typography>

      {/* Filters */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <Autocomplete
              multiple
              size="small"
              options={getUniqueValues('type')}
              value={filters.type}
              onChange={(event, newValue) => handleFilterChange('type', newValue)}
              renderInput={(params) => (
                <TextField {...params} label="Type" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    {...getTagProps({ index })}
                    key={option}
                    label={option}
                    size="small"
                  />
                ))
              }
              sx={{ minWidth: 200 }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Autocomplete
              multiple
              size="small"
              options={getUniqueValues('city')}
              value={filters.city}
              onChange={(event, newValue) => handleFilterChange('city', newValue)}
              renderInput={(params) => (
                <TextField {...params} label="City" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    {...getTagProps({ index })}
                    key={option}
                    label={option}
                    size="small"
                  />
                ))
              }
              sx={{ minWidth: 150 }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Autocomplete
              multiple
              size="small"
              options={getUniqueValues('country')}
              value={filters.country}
              onChange={(event, newValue) => handleFilterChange('country', newValue)}
              renderInput={(params) => (
                <TextField {...params} label="Country" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    {...getTagProps({ index })}
                    key={option}
                    label={option}
                    size="small"
                  />
                ))
              }
              sx={{ minWidth: 150 }}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <Autocomplete
              multiple
              size="small"
              options={getUniqueValues('tags')}
              value={filters.tag}
              onChange={(event, newValue) => handleFilterChange('tag', newValue)}
              renderInput={(params) => (
                <TextField {...params} label="Tag" />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    {...getTagProps({ index })}
                    key={option}
                    label={option}
                    size="small"
                  />
                ))
              }
              sx={{ minWidth: 200 }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControlLabel
              control={
                <Switch
                  checked={filters.starred}
                  onChange={(event) => handleFilterChange('starred', event.target.checked)}
                  color="primary"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Star color={filters.starred ? 'warning' : 'action'} />
                  <Typography variant="body2">Starred Only</Typography>
                </Box>
              }
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant="outlined"
              onClick={clearFilters}
              fullWidth
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Results Summary */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Entities ({entities.length})
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchEntities}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Entities Table */}
      {!loading && !error && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={sortConfig.key === 'name'}
                    direction={sortConfig.direction}
                    onClick={() => handleSort('name')}
                  >
                    <strong>Name</strong>
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortConfig.key === 'type'}
                    direction={sortConfig.direction}
                    onClick={() => handleSort('type')}
                  >
                    <strong>Type</strong>
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortConfig.key === 'city'}
                    direction={sortConfig.direction}
                    onClick={() => handleSort('city')}
                  >
                    <strong>City</strong>
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortConfig.key === 'country'}
                    direction={sortConfig.direction}
                    onClick={() => handleSort('country')}
                  >
                    <strong>Country</strong>
                  </TableSortLabel>
                </TableCell>
                <TableCell><strong>Tags</strong></TableCell>
                <TableCell><strong>Star</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedEntities.length > 0 ? (
                sortedEntities.map((entity) => (
                  <TableRow key={entity.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {entity.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={entity.type} 
                        size="small" 
                        color="primary" 
                        variant="outlined" 
                      />
                    </TableCell>
                    <TableCell>
                      {entity.city}
                    </TableCell>
                    <TableCell>
                      {entity.country}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, alignItems: 'center' }}>
                        {entity.tags && entity.tags.map((tag) => (
                          <Chip 
                            key={tag.id} 
                            label={tag.name} 
                            size="small" 
                            variant="outlined"
                            sx={{ fontSize: '0.7rem' }}
                            onClick={() => setRemoveTagDialog({ open: true, entity: entity, tag: tag })}
                          />
                        ))}
                        <IconButton 
                          size="small" 
                          onClick={() => setAddTagDialog({ open: true, entity: entity })}
                          sx={{ ml: 0.5 }}
                        >
                          <Add fontSize="small" />
                        </IconButton>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        size="small"
                        onClick={() => handleToggleStar(entity.id, entity.is_starred)}
                      >
                        {entity.is_starred ? (
                          <Star sx={{ color: 'warning.main' }} />
                        ) : (
                          <StarBorder />
                        )}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        size="small"
                        onClick={() => setEditDialog({ open: true, entity: entity })}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton 
                        size="small"
                        onClick={() => setDeleteDialog({ open: true, entity: entity })}
                        sx={{ ml: 1 }}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No entities found matching the current filters.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add Tag Dialog */}
      <Dialog 
        open={addTagDialog.open} 
        onClose={() => setAddTagDialog({ open: false, entity: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Tag to {addTagDialog.entity?.name}</DialogTitle>
        <DialogContent>
          <Autocomplete
            options={filterOptions.tags || []}
            renderInput={(params) => (
              <TextField {...params} label="Select Tag" margin="dense" />
            )}
            onChange={(event, newValue) => {
              if (newValue && addTagDialog.entity) {
                handleAddTag(addTagDialog.entity.id, newValue);
                setAddTagDialog({ open: false, entity: null });
              }
            }}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddTagDialog({ open: false, entity: null })}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Remove Tag Confirmation Dialog */}
      <Dialog 
        open={removeTagDialog.open} 
        onClose={() => setRemoveTagDialog({ open: false, entity: null, tag: null })}
      >
        <DialogTitle>Remove Tag</DialogTitle>
        <DialogContent>
          <Typography>
            Remove tag "{removeTagDialog.tag?.name}" from {removeTagDialog.entity?.name}?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveTagDialog({ open: false, entity: null, tag: null })}>
            Cancel
          </Button>
          <Button 
            onClick={() => {
              if (removeTagDialog.entity && removeTagDialog.tag) {
                handleRemoveTag(removeTagDialog.entity.id, removeTagDialog.tag.name);
              }
              setRemoveTagDialog({ open: false, entity: null, tag: null });
            }}
            color="error"
          >
            Remove
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Entity Dialog */}
      <Dialog 
        open={editDialog.open} 
        onClose={() => setEditDialog({ open: false, entity: null })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Entity</DialogTitle>
        <DialogContent>
          <TextField
            label="Entity ID"
            value={editDialog.entity?.id || ''}
            fullWidth
            margin="dense"
            InputProps={{
              readOnly: true,
            }}
          />
          <TextField
            label="Name"
            value={editFormData.name}
            onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
            fullWidth
            margin="dense"
            required
          />
          <FormControl fullWidth margin="dense" required>
            <InputLabel>Type</InputLabel>
            <Select
              value={editFormData.type}
              onChange={(e) => setEditFormData({ ...editFormData, type: e.target.value })}
              label="Type"
            >
              {validEntityTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="City"
            value={editFormData.city}
            onChange={(e) => setEditFormData({ ...editFormData, city: e.target.value })}
            fullWidth
            margin="dense"
            required
          />
          <TextField
            label="Country"
            value={editFormData.country}
            onChange={(e) => setEditFormData({ ...editFormData, country: e.target.value })}
            fullWidth
            margin="dense"
            required
          />
          <TextField
            label="Description"
            value={editFormData.description}
            onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
            fullWidth
            margin="dense"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, entity: null })}>
            Cancel
          </Button>
          <Button 
            onClick={() => {
              handleEditEntity(editDialog.entity.id, editFormData);
              setEditDialog({ open: false, entity: null });
            }}
            variant="contained"
            disabled={!editFormData.name.trim() || !editFormData.type || !editFormData.city.trim() || !editFormData.country.trim()}
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Entity Confirmation Dialog */}
      <Dialog 
        open={deleteDialog.open} 
        onClose={() => setDeleteDialog({ open: false, entity: null })}
      >
        <DialogTitle>Delete Entity</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{deleteDialog.entity?.name}"? This action cannot be undone.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This will also remove all associated tags and relationships.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, entity: null })}>
            Cancel
          </Button>
          <Button 
            onClick={() => {
              if (deleteDialog.entity) {
                handleDeleteEntity(deleteDialog.entity.id);
              }
              setDeleteDialog({ open: false, entity: null });
            }}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ExploreTab;

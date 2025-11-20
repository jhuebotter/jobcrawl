// frontend/src/components/SearchTab.jsx
import React from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
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
} from '@mui/material';
import {
  ArrowUpward,
  ArrowDownward,
  Close,
  Info,
} from '@mui/icons-material';
import MapComponent from './MapComponent';

function SearchTab({
  location,
  position,
  searchQuery,
  setSearchQuery,
  handleSearch,
  options,
  descriptions,
  selectedOptions,
  setSelectedOptions,
  tags,
  selectedTags,
  setSelectedTags,
  handleAddToList,
  handleExport,
  locationList,
  setLocationList,
  sortBy,
  sortOrder,
  handleSort,
  sortedLocationList,
  // 👇 these were missing
  setLocation,
  setPosition,
}) {
  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome to JobCrawler
      </Typography>
      <Typography variant="body1" paragraph>
        Add places to the list to explore local organizations
      </Typography>

      {/* Search bar */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={9}>
          <TextField
            label="Search for a location"
            variant="outlined"
            fullWidth
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </Grid>
        <Grid item xs={3}>
          <Button
            variant="contained"
            onClick={handleSearch}
            fullWidth
            sx={{ height: '100%' }}
          >
            Search
          </Button>
        </Grid>
      </Grid>

      {/* Map + organization types + tags */}
      <Box sx={{ display: 'flex', mb: 2 }}>
        <Box sx={{ flex: 2, height: '400px' }}>
          <MapComponent
            setLocation={setLocation}
            setPosition={setPosition}
            position={position}
          />
        </Box>
        <Box sx={{ flex: 1, pl: 2, display: 'flex', gap: 3 }}>
          {/* Organizations Section */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Organizations
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column' }}>
              {options.map((option) => (
                <FormControlLabel
                  key={option}
                  control={
                    <Checkbox
                      checked={selectedOptions.includes(option)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedOptions([...selectedOptions, option]);
                        } else {
                          if (selectedOptions.length > 1) {
                            setSelectedOptions(
                              selectedOptions.filter((o) => o !== option),
                            );
                          }
                        }
                      }}
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {option}
                      <Tooltip title={descriptions[option]}>
                        <Info
                          sx={{
                            fontSize: 16,
                            ml: 1,
                            color: 'text.secondary',
                          }}
                        />
                      </Tooltip>
                    </Box>
                  }
                />
              ))}
            </Box>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  if (selectedOptions.length < options.length) {
                    setSelectedOptions([...options]);
                  }
                }}
                disabled={selectedOptions.length === options.length}
              >
                Select All
              </Button>
            </Box>
          </Box>

          {/* Tags Section */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Tags
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column' }}>
              {tags && tags.map((tag) => (
                <FormControlLabel
                  key={tag.id}
                  control={
                    <Checkbox
                      checked={selectedTags.includes(tag.name)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedTags([...selectedTags, tag.name]);
                        } else {
                          if (selectedTags.length > 1) {
                            setSelectedTags(
                              selectedTags.filter((t) => t !== tag.name),
                            );
                          }
                        }
                      }}
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {tag.name}
                      {tag.description && (
                        <Tooltip title={tag.description}>
                          <Info
                            sx={{
                              fontSize: 16,
                              ml: 1,
                              color: 'text.secondary',
                            }}
                          />
                        </Tooltip>
                      )}
                    </Box>
                  }
                />
              ))}
            </Box>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  if (selectedTags.length < tags.length) {
                    setSelectedTags(tags.map(tag => tag.name));
                  }
                }}
                disabled={selectedTags.length === tags.length}
              >
                Select All
              </Button>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* City / country / list actions */}
      <Grid container spacing={2} sx={{ mt: 2, mb: 4 }}>
        <Grid item xs={12} sm={3}>
          <TextField
            label="City"
            variant="outlined"
            fullWidth
            value={location.city}
            InputProps={{
              readOnly: true,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <TextField
            label="Country"
            variant="outlined"
            fullWidth
            value={location.country}
            InputProps={{
              readOnly: true,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <Button
            variant="contained"
            onClick={handleAddToList}
            fullWidth
            sx={{ height: '100%' }}
          >
            Add to List
          </Button>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Button
            variant="outlined"
            onClick={handleExport}
            fullWidth
            sx={{ height: '100%' }}
          >
            Export List
          </Button>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Button
            variant="outlined"
            onClick={() => setLocationList([])}
            fullWidth
            sx={{ height: '100%' }}
          >
            Clear List
          </Button>
        </Grid>
      </Grid>

      {/* Location list */}
      <Typography variant="h5" component="h2" gutterBottom>
        Location List
      </Typography>
      <TableContainer component={Paper}>
        <Table sx={{ tableLayout: 'fixed' }}>
          <TableHead>
            <TableRow>
              <TableCell
                onClick={() => handleSort('city')}
                sx={{ cursor: 'pointer', width: '45%' }}
              >
                City
                {sortBy === 'city' &&
                  (sortOrder === 'asc' ? (
                    <ArrowUpward fontSize="small" />
                  ) : (
                    <ArrowDownward fontSize="small" />
                  ))}
              </TableCell>
              <TableCell
                onClick={() => handleSort('country')}
                sx={{ cursor: 'pointer', width: '45%' }}
              >
                Country
                {sortBy === 'country' &&
                  (sortOrder === 'asc' ? (
                    <ArrowUpward fontSize="small" />
                  ) : (
                    <ArrowDownward fontSize="small" />
                  ))}
              </TableCell>
              <TableCell sx={{ width: '10%' }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedLocationList.map((loc, index) => (
              <TableRow
                key={index}
                sx={{ '&:hover .delete-button': { opacity: 1 } }}
              >
                <TableCell sx={{ width: '45%' }}>{loc.city}</TableCell>
                <TableCell sx={{ width: '45%' }}>{loc.country}</TableCell>
                <TableCell
                  sx={{
                    width: '10%',
                    position: 'relative',
                    overflow: 'visible',
                  }}
                >
                  <IconButton
                    className="delete-button"
                    onClick={() =>
                      setLocationList(
                        locationList.filter((_, i) => i !== index),
                      )
                    }
                    sx={{
                      position: 'absolute',
                      right: 8,
                      top: '50%',
                      transform: 'translateY(-50%)',
                      opacity: 0,
                      transition: 'opacity 0.2s',
                      '&:hover': {
                        backgroundColor: 'rgba(0,0,0,0.04)',
                      },
                    }}
                  >
                    <Close />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default SearchTab;

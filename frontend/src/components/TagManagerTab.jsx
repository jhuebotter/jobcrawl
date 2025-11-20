// frontend/src/components/TagManagerTab.jsx
import React from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
} from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';

function TagManagerTab({
  newTagName,
  setNewTagName,
  newTagDescription,
  setNewTagDescription,
  handleAddTag,
  tags,
  getTagEntityCount,
  openEditDialog,
  openDeleteDialog,
}) {
  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Tag Manager
      </Typography>
      <Typography variant="body1" paragraph>
        Manage tags for categorizing organizations.
      </Typography>

      {/* Add new tag */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6">Add New Tag</Typography>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Tag Name"
              variant="outlined"
              fullWidth
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Description (optional)"
              variant="outlined"
              fullWidth
              value={newTagDescription}
              onChange={(e) => setNewTagDescription(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant="contained"
              onClick={handleAddTag}
              fullWidth
              sx={{ height: '100%' }}
            >
              Add Tag
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* List of tags */}
      <Typography variant="h6">Existing Tags</Typography>
      <List>
        {tags && tags.length > 0 ? (
          tags.map((tag) => {
            const entityCount = getTagEntityCount ? getTagEntityCount(tag.id) : 0;
            return (
              <ListItem key={tag.id} divider>
                <ListItemText
                  primary={tag.name}
                  secondary={
                    `${tag.description ? tag.description + ' • ' : ''}ID: ${tag.id} • ${entityCount} ${entityCount === 1 ? 'entity' : 'entities'}`
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton onClick={() => openEditDialog(tag)}>
                    <Edit />
                  </IconButton>
                  <IconButton onClick={() => openDeleteDialog(tag)}>
                    <Delete />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            );
          })
        ) : (
          <ListItem>
            <ListItemText primary="No tags yet." />
          </ListItem>
        )}
      </List>
    </Box>
  );
}

export default TagManagerTab;

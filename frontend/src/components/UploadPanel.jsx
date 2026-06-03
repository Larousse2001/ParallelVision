import React from "react";
import {
  Box,
  Button,
  Stack,
  Typography,
  TextField,
  Chip,
} from "@mui/material";

const UploadPanel = ({
  selectedFiles,
  onSelectFiles,
  onUpload,
  onStart,
  processes,
  threads,
  setProcesses,
  setThreads,
  isRunning,
  hasUploaded,
}) => {
  return (
    <Box className="panel">
      <Typography variant="h6" gutterBottom>
        Chargement des images
      </Typography>
      <Stack spacing={2}>
        <Button variant="contained" component="label">
          Choisir des images
          <input
            hidden
            type="file"
            accept="image/*"
            multiple
            onChange={(event) => onSelectFiles(Array.from(event.target.files))}
          />
        </Button>
        <Typography variant="body2">
          {selectedFiles.length} fichiers selectionnes
        </Typography>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <TextField
            label="Processus"
            type="number"
            value={processes}
            onChange={(event) => setProcesses(Number(event.target.value))}
            inputProps={{ min: 1 }}
          />
          <TextField
            label="Threads"
            type="number"
            value={threads}
            onChange={(event) => setThreads(Number(event.target.value))}
            inputProps={{ min: 1 }}
          />
        </Stack>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <Button
            variant="outlined"
            onClick={onUpload}
            disabled={!selectedFiles.length}
          >
            Uploader
          </Button>
          <Button
            variant="contained"
            onClick={onStart}
            disabled={!hasUploaded || isRunning}
          >
            Demarrer le traitement
          </Button>
        </Stack>
        {isRunning ? <Chip color="secondary" label="Traitement en cours" /> : null}
      </Stack>
    </Box>
  );
};

export default UploadPanel;

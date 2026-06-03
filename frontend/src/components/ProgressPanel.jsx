import React from "react";
import { Box, LinearProgress, Stack, Typography } from "@mui/material";

const ProgressPanel = ({ status }) => {
  const progress = status.total_images
    ? (status.processed_images / status.total_images) * 100
    : 0;

  return (
    <Box className="panel">
      <Typography variant="h6" gutterBottom>
        Progression
      </Typography>
      <Stack spacing={2}>
        <LinearProgress variant="determinate" value={progress} />
        <Typography variant="body2">
          {status.processed_images} / {status.total_images} images traitees
        </Typography>
        <Typography variant="body2">
          Etat: {status.state}
        </Typography>
      </Stack>
    </Box>
  );
};

export default ProgressPanel;

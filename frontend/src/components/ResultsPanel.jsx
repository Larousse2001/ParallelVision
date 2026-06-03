import React from "react";
import { Box, Chip, Stack, Typography } from "@mui/material";

const ResultsPanel = ({ results }) => {
  return (
    <Box className="panel">
      <Typography variant="h6" gutterBottom>
        Resultats
      </Typography>
      {results.length === 0 ? (
        <Typography variant="body2">Aucun resultat pour le moment.</Typography>
      ) : (
        <div className="image-grid">
          {results.map((item) => (
            <Box key={item.image_id} className="image-card">
              <Stack spacing={1}>
                <Typography variant="subtitle2" noWrap title={item.image_id}>
                  {item.image_id.slice(0, 8)}…
                </Typography>

                {/* Grayscale */}
                <Typography variant="caption" color="text.secondary">
                  Niveaux de gris
                </Typography>
                <img
                  src={`data:image/png;base64,${item.images.gray}`}
                  alt="gray"
                  style={{ width: "100%", borderRadius: 4 }}
                />

                {/* Edges */}
                <Typography variant="caption" color="text.secondary">
                  Contours (Canny)
                </Typography>
                <img
                  src={`data:image/png;base64,${item.images.edges}`}
                  alt="edges"
                  style={{ width: "100%", borderRadius: 4 }}
                />

                {/* Face-annotated */}
                <Typography variant="caption" color="text.secondary">
                  Detection de visages
                </Typography>
                <Box sx={{ position: "relative" }}>
                  <img
                    src={`data:image/png;base64,${item.images.faces_annotated}`}
                    alt="faces"
                    style={{ width: "100%", borderRadius: 4 }}
                  />
                  {item.faces > 0 && (
                    <Chip
                      label={`${item.faces} visage${item.faces > 1 ? "s" : ""}`}
                      color="success"
                      size="small"
                      sx={{ position: "absolute", top: 4, right: 4, fontSize: 10 }}
                    />
                  )}
                </Box>

                <Typography variant="caption">
                  Visages: {item.faces} | Contours: {item.contour_count ?? "—"} | Temps:{" "}
                  {item.duration_ms.toFixed(2)} ms
                </Typography>
              </Stack>
            </Box>
          ))}
        </div>
      )}
    </Box>
  );
};

export default ResultsPanel;

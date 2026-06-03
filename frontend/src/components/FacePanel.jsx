import React, { useMemo } from "react";
import {
  Box,
  Chip,
  Grid,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";

/**
 * FacePanel
 *
 * Shows a gallery of only the images where at least one face was detected,
 * plus a simple horizontal bar chart summarising face counts across all
 * processed images.  No new API endpoint required — it consumes the same
 * `results` prop as ResultsPanel.
 */
const FacePanel = ({ results }) => {
  const withFaces = useMemo(
    () => results.filter((r) => r.faces > 0),
    [results]
  );

  const totalFaces = useMemo(
    () => results.reduce((sum, r) => sum + r.faces, 0),
    [results]
  );

  const maxFaces = useMemo(
    () => Math.max(1, ...results.map((r) => r.faces)),
    [results]
  );

  if (results.length === 0) {
    return (
      <Box className="panel">
        <Typography variant="h6" gutterBottom>
          Analyse des visages
        </Typography>
        <Typography variant="body2">
          Aucune image traitee pour le moment.
        </Typography>
      </Box>
    );
  }

  return (
    <Box className="panel">
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <Typography variant="h6">Analyse des visages</Typography>
        <Chip
          label={`${totalFaces} visage${totalFaces !== 1 ? "s" : ""} detecte${totalFaces !== 1 ? "s" : ""}`}
          color={totalFaces > 0 ? "success" : "default"}
          size="small"
        />
        <Chip
          label={`${withFaces.length} / ${results.length} images`}
          variant="outlined"
          size="small"
        />
      </Stack>

      {/* ── Bar chart ─────────────────────────────────────────────────── */}
      <Typography variant="subtitle2" gutterBottom>
        Nombre de visages par image
      </Typography>
      <Box
        sx={{
          display: "flex",
          alignItems: "flex-end",
          gap: "3px",
          height: 60,
          mb: 3,
          overflowX: "auto",
          py: 0.5,
        }}
      >
        {results.map((item) => {
          const pct = (item.faces / maxFaces) * 100;
          const label = item.image_id.slice(0, 4);
          return (
            <Tooltip
              key={item.image_id}
              title={`${item.faces} visage${item.faces !== 1 ? "s" : ""}`}
            >
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  minWidth: 18,
                  flex: "1 0 18px",
                  maxWidth: 40,
                }}
              >
                <Box
                  sx={{
                    width: "100%",
                    height: `${Math.max(4, pct * 0.52)}px`,
                    bgcolor: item.faces > 0 ? "success.main" : "grey.300",
                    borderRadius: "2px 2px 0 0",
                    transition: "height 0.4s ease",
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{ fontSize: 8, color: "text.disabled", mt: 0.2 }}
                >
                  {label}
                </Typography>
              </Box>
            </Tooltip>
          );
        })}
      </Box>

      {/* ── Gallery of detected faces ──────────────────────────────────── */}
      <Typography variant="subtitle2" gutterBottom>
        Images avec visages detectes
      </Typography>
      {withFaces.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          Aucun visage detecte dans le lot.
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {withFaces.map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.image_id}>
              <Box
                sx={{
                  border: "1px solid",
                  borderColor: "success.light",
                  borderRadius: 2,
                  overflow: "hidden",
                  position: "relative",
                  bgcolor: "background.paper",
                }}
              >
                <img
                  src={`data:image/png;base64,${item.images.faces_annotated}`}
                  alt={`faces-${item.image_id}`}
                  style={{ width: "100%", display: "block" }}
                />
                <Box
                  sx={{
                    px: 1,
                    py: 0.5,
                    bgcolor: "success.light",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Typography variant="caption" color="success.dark">
                    {item.faces} visage{item.faces > 1 ? "s" : ""}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.duration_ms.toFixed(1)} ms
                  </Typography>
                </Box>

                {/* Bounding-box metadata list */}
                {item.faces_bboxes && item.faces_bboxes.length > 0 && (
                  <Box sx={{ px: 1, py: 0.5 }}>
                    {item.faces_bboxes.map(([x, y, w, h], idx) => (
                      <Typography
                        key={idx}
                        variant="caption"
                        display="block"
                        color="text.secondary"
                      >
                        #{idx + 1}: x={x} y={y} {w}×{h}px
                      </Typography>
                    ))}
                  </Box>
                )}
              </Box>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default FacePanel;

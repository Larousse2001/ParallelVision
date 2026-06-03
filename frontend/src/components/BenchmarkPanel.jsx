import React from "react";
import {
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

const BenchmarkPanel = ({ rows, onRun }) => {
  return (
    <Box className="panel">
      <Typography variant="h6" gutterBottom>
        Benchmarking
      </Typography>
      <Button variant="outlined" onClick={onRun} sx={{ mb: 2 }}>
        Lancer le benchmark
      </Button>
      {rows.length === 0 ? (
        <Typography variant="body2">Aucun benchmark disponible.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Processus</TableCell>
              <TableCell>Threads</TableCell>
              <TableCell>Temps total (s)</TableCell>
              <TableCell>Temps moyen (ms)</TableCell>
              <TableCell>CPU (%)</TableCell>
              <TableCell>Speedup</TableCell>
              <TableCell>Efficacite</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={`${row.processes}-${row.threads}`}>
                <TableCell>{row.processes}</TableCell>
                <TableCell>{row.threads}</TableCell>
                <TableCell>{row.total_time_s.toFixed(2)}</TableCell>
                <TableCell>{row.avg_time_ms.toFixed(2)}</TableCell>
                <TableCell>{row.cpu_usage_pct.toFixed(1)}</TableCell>
                <TableCell>{row.speedup.toFixed(2)}</TableCell>
                <TableCell>{row.efficiency.toFixed(3)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Box>
  );
};

export default BenchmarkPanel;

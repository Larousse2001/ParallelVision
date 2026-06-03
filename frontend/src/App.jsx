import React, { useEffect, useState } from "react";
import { Container, Grid, Stack, Typography } from "@mui/material";

import UploadPanel from "./components/UploadPanel.jsx";
import ProgressPanel from "./components/ProgressPanel.jsx";
import ResultsPanel from "./components/ResultsPanel.jsx";
import FacePanel from "./components/FacePanel.jsx";
import BenchmarkPanel from "./components/BenchmarkPanel.jsx";
import {
  uploadImages,
  startProcessing,
  fetchStatus,
  fetchResults,
  fetchBenchmark,
} from "./api.js";

const App = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploaded, setUploaded] = useState(false);
  const [status, setStatus] = useState({
    state: "idle",
    total_images: 0,
    processed_images: 0,
    in_flight: 0,
  });
  const [results, setResults] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [processes, setProcesses] = useState(8);
  const [threads, setThreads] = useState(8);

  const handleUpload = async () => {
    const response = await uploadImages(selectedFiles);
    setUploaded(response.total_images > 0);
    setStatus((prev) => ({
      ...prev,
      total_images: response.total_images,
      processed_images: 0,
    }));
  };

  const handleStart = async () => {
    await startProcessing(processes, threads);
    const latestStatus = await fetchStatus();
    setStatus(latestStatus);
  };

  const handleBenchmark = async () => {
    const response = await fetchBenchmark(true);
    setBenchmarks(response.rows || []);
  };

  useEffect(() => {
    if (status.state !== "running") {
      return undefined;
    }

    const interval = setInterval(async () => {
      const latest = await fetchStatus();
      setStatus(latest);
      if (latest.state === "completed") {
        const resultResponse = await fetchResults();
        setResults(resultResponse.results || []);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [status.state]);

  return (
    <div className="app-shell">
      <Container maxWidth="lg" className="content">
        <Stack spacing={3}>
          <Typography variant="h2">Parallel Vision</Typography>
          <Typography variant="subtitle1">
            Traitement parallele d images avec IPC, detection de visages et benchmarking.
          </Typography>
        </Stack>

        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12} md={5}>
            <UploadPanel
              selectedFiles={selectedFiles}
              onSelectFiles={setSelectedFiles}
              onUpload={handleUpload}
              onStart={handleStart}
              processes={processes}
              threads={threads}
              setProcesses={setProcesses}
              setThreads={setThreads}
              isRunning={status.state === "running"}
              hasUploaded={uploaded}
            />
          </Grid>
          <Grid item xs={12} md={7}>
            <ProgressPanel status={status} />
          </Grid>
          <Grid item xs={12}>
            <FacePanel results={results} />
          </Grid>
          <Grid item xs={12}>
            <ResultsPanel results={results} />
          </Grid>
          <Grid item xs={12}>
            <BenchmarkPanel rows={benchmarks} onRun={handleBenchmark} />
          </Grid>
        </Grid>
      </Container>
    </div>
  );
};

export default App;

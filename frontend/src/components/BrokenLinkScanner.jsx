import { useState } from "react";
import axios from "axios";
import {
  Card, CardHeader, CardContent,
  Box, Button, TextField, Grid, Chip,
  LinearProgress, Typography, Table, TableHead,
  TableRow, TableCell, TableBody, TableContainer, Paper
} from "@mui/material";
import { API_BASE_URL } from "../api";

export default function BrokenLinkScanner({ defaultRoot }) {
  const [startUrl, setStartUrl] = useState(defaultRoot || "");
  const [maxPages, setMaxPages] = useState(50);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);

  const handleScan = async () => {
    try {
      setErr(null);
      setLoading(true);
      const params = new URLSearchParams();
      if (startUrl) params.set("start_url", startUrl);
      params.set("max_pages", String(maxPages));
      const { data } = await axios.get(`${API_BASE_URL}/linkscan?${params.toString()}`);
      setResult(data);
    } catch (e) {
      setErr(e?.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const disabled = loading || maxPages < 1 || maxPages > 50;

  return (
    <Card>
      <CardHeader
        title={
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Broken Link Scanner (up to 50 pages)
            </Typography>
          </Box>
        }
        subheader="Crawls same-domain pages (BFS), checks links with HEAD/GET"
      />
      <CardContent>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} md={7}>
            <TextField
              label="Start URL (optional — defaults to monitored site)"
              fullWidth
              value={startUrl}
              onChange={(e) => setStartUrl(e.target.value)}
              placeholder={defaultRoot || "https://example.com"}
            />
          </Grid>
          <Grid item xs={8} md={3}>
            <TextField
              label="Max pages"
              type="number"
              fullWidth
              inputProps={{ min: 1, max: 50 }}
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
            />
          </Grid>
          <Grid item xs={4} md={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleScan}
              disabled={disabled}
            >
              {loading ? "Scanning..." : "Run scan"}
            </Button>
          </Grid>
        </Grid>

        {loading && <LinearProgress sx={{ mt: 2 }} />}

        {err && (
          <Typography color="error" sx={{ mt: 2 }}>
            {err}
          </Typography>
        )}

        {result && (
          <Box sx={{ mt: 3, display: "grid", gap: 2 }}>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Chip label={`Scanned pages: ${result.scanned_count}`} />
              <Chip label={`Total links checked: ${result.total_links_checked}`} />
              <Chip color="success" label={`OK: ${result.ok_count}`} />
              <Chip color={result.broken_count > 0 ? "error" : "success"} label={`Broken: ${result.broken_count}`} />
              <Chip label={`Skipped (non-http): ${result.skipped_non_http}`} />
              <Chip label={`Time: ${result.duration_ms} ms`} />
            </Box>

            <Typography variant="body2" color="text.secondary">
              Start URL: <b>{result.start_url}</b>
            </Typography>

            <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Source Page</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Broken Link</TableCell>
                    <TableCell sx={{ fontWeight: 700, width: 120 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700, width: 240 }}>Error</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {result.broken?.length > 0 ? (
                    result.broken.slice(0, 200).map((row, idx) => (
                      <TableRow key={idx}>
                        <TableCell sx={{ wordBreak: "break-all" }}>{row.source_page}</TableCell>
                        <TableCell sx={{ wordBreak: "break-all" }}>{row.link}</TableCell>
                        <TableCell>{row.status_code ?? "n/a"}</TableCell>
                        <TableCell sx={{ wordBreak: "break-all" }}>{row.error ?? ""}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={4}>
                        <Typography>No broken links found 🎉</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {result.scanned_pages?.length > 0 && (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>
                  Scanned pages ({result.scanned_pages.length})
                </Typography>
                <Box sx={{ display: "grid", gap: 0.5 }}>
                  {result.scanned_pages.map((p, i) => (
                    <Typography key={i} variant="caption" sx={{ wordBreak: "break-all" }}>
                      {p}
                    </Typography>
                  ))}
                </Box>
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

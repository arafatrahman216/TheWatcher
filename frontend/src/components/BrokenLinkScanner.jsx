import { useState } from "react";
import axios from "axios";
import {
  Card, CardHeader, CardContent,
  Box, Button, TextField, Grid, Chip,
  LinearProgress, Typography, Table, TableHead,
  TableRow, TableCell, TableBody, TableContainer, Paper,
  Stack, Divider, Collapse, IconButton, Tooltip, Slider, ButtonGroup
} from "@mui/material";
import {
  LinkOff, Link as LinkIcon, QueryStats, Timer, ExpandMore, ExpandLess, TravelExplore
} from "@mui/icons-material";
import { API_BASE_URL } from "../api";

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

export default function BrokenLinkScanner({ defaultRoot }) {
  // keep input as string to avoid leading-zero quirks; allow empty while typing
  const [maxPagesStr, setMaxPagesStr] = useState("50");
  const [sliderValue, setSliderValue] = useState(50);

  const [startUrl, setStartUrl] = useState(defaultRoot || "");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [showPages, setShowPages] = useState(false);

  // derive effective maxPages safely
  const parsed = maxPagesStr === "" ? NaN : parseInt(maxPagesStr, 10);
  const effectiveMax = Number.isFinite(parsed) ? clamp(parsed, 1, 50) : sliderValue;
  const disabled = loading || effectiveMax < 1 || effectiveMax > 50;

  // ========== FIXED INPUT HANDLERS ==========
  const handleMaxPagesInput = (e) => {
    // allow empty while typing
    const raw = e.target.value ?? "";
    const digitsOnly = raw.replace(/\D+/g, ""); // strip non-digits
    setMaxPagesStr(digitsOnly);                 // can be '' temporarily

    // only sync slider if we have a number
    if (digitsOnly !== "") {
      const n = clamp(parseInt(digitsOnly, 10) || 1, 1, 50);
      setSliderValue(n);
    }
  };

  const handleMaxPagesBlur = () => {
    // on blur, normalize empty -> current slider value, then clamp
    if (maxPagesStr === "") {
      setMaxPagesStr(String(sliderValue));
      return;
    }
    const n = clamp(parseInt(maxPagesStr, 10) || 1, 1, 50);
    setMaxPagesStr(String(n));
    setSliderValue(n);
  };

  const handleSlider = (_, value) => {
    const v = Array.isArray(value) ? value[0] : value;
    setSliderValue(v);
    setMaxPagesStr(String(v)); // keep inputs in sync
  };

  const setPreset = (v) => {
    const n = clamp(v, 1, 50);
    setMaxPagesStr(String(n));
    setSliderValue(n);
  };
  // ==========================================

  const handleScan = async () => {
    try {
      setErr(null);
      setLoading(true);
      setResult(null);

      // final guard: clamp just before request
      const maxPages = clamp(
        Number.isFinite(parsed) ? parsed : sliderValue,
        1, 50
      );

      const params = new URLSearchParams();
      if (startUrl.trim()) params.set("start_url", startUrl.trim());
      params.set("max_pages", String(maxPages));

      const { data } = await axios.get(`${API_BASE_URL}/linkscan?${params.toString()}`);
      setResult(data);
    } catch (e) {
      setErr(e?.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ overflow: "hidden" }}>
      <CardHeader
        title={
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <TravelExplore color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Broken Link Scanner
            </Typography>
          </Box>
        }
        subheader="Crawls same-domain pages (BFS) up to 50 pages and checks links via HEAD/GET"
      />

      <CardContent>
        {/* Controls */}
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={7}>
            <TextField
              label="Start URL"
              fullWidth
              value={startUrl}
              onChange={(e) => setStartUrl(e.target.value)}
              placeholder={defaultRoot || "https://example.com"}
              helperText="Leave blank to use the monitored website URL"
            />
          </Grid>

          <Grid item xs={12} md={5}>
            <Stack spacing={1}>
              <Stack direction="row" spacing={1} alignItems="center">
                <TextField
                  label="Max pages"
                  value={maxPagesStr}
                  onChange={handleMaxPagesInput}
                  onBlur={handleMaxPagesBlur}
                  inputProps={{ inputMode: "numeric", pattern: "[0-9]*" }}
                  sx={{ width: 140 }}
                  placeholder="1–50"
                />
                <ButtonGroup variant="outlined" size="small" sx={{ ml: 1 }}>
                  <Button onClick={() => setPreset(10)}>10</Button>
                  <Button onClick={() => setPreset(25)}>25</Button>
                  <Button onClick={() => setPreset(50)}>50</Button>
                </ButtonGroup>
                <Box sx={{ flexGrow: 1 }} />
                <Button
                  variant="contained"
                  onClick={handleScan}
                  disabled={disabled}
                  sx={{ minWidth: 140, fontWeight: 700 }}
                >
                  {loading ? "Scanning…" : "Run scan"}
                </Button>
              </Stack>

              <Slider
                value={sliderValue}
                min={1}
                max={50}
                step={1}
                onChange={handleSlider}
                valueLabelDisplay="auto"
                marks={[{ value: 1 }, { value: 10 }, { value: 25 }, { value: 50 }]}
                sx={{ mt: 1 }}
              />
            </Stack>
          </Grid>
        </Grid>

        {loading && <LinearProgress sx={{ mt: 2, borderRadius: 1 }} />}

        {err && (
          <Typography color="error" sx={{ mt: 2 }}>
            {err}
          </Typography>
        )}

        {/* Results */}
        {result && (
          <Box sx={{ mt: 3 }}>
            {/* Summary chips */}
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                borderRadius: 2,
                background:
                  result.broken_count > 0
                    ? "linear-gradient(135deg, #fee2e2 0%, #fff 100%)"
                    : "linear-gradient(135deg, #ecfdf5 0%, #fff 100%)",
              }}
            >
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip
                  icon={<QueryStats />}
                  label={`Scanned pages: ${result.scanned_count}/${result.max_pages}`}
                  variant="filled"
                />
                <Chip
                  icon={<LinkIcon />}
                  label={`Checked: ${result.total_links_checked}`}
                  variant="outlined"
                />
                <Chip color="success" label={`OK: ${result.ok_count}`} variant="filled" />
                <Chip
                  icon={<LinkOff />}
                  color={result.broken_count > 0 ? "error" : "success"}
                  label={`Broken: ${result.broken_count}`}
                  variant="filled"
                />
                <Chip label={`Skipped (non-http): ${result.skipped_non_http}`} variant="outlined" />
                <Chip icon={<Timer />} label={`${result.duration_ms} ms`} variant="outlined" />
              </Stack>

              <Typography variant="body2" sx={{ mt: 1.5 }} color="text.secondary">
                Start URL: <b style={{ wordBreak: "break-all" }}>{result.start_url}</b>
              </Typography>
            </Paper>

            {/* Broken links table */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1 }}>
                Broken links
              </Typography>
              <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700, width: "34%" }}>Source Page</TableCell>
                      <TableCell sx={{ fontWeight: 700, width: "46%" }}>Broken Link</TableCell>
                      <TableCell sx={{ fontWeight: 700, width: "10%" }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 700, width: "10%" }}>Error</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {result.broken?.length > 0 ? (
                      result.broken.slice(0, 300).map((row, idx) => (
                        <TableRow key={idx} hover>
                          <TableCell sx={{ wordBreak: "break-all" }}>{row.source_page}</TableCell>
                          <TableCell sx={{ wordBreak: "break-all" }}>{row.link}</TableCell>
                          <TableCell>{row.status_code ?? "n/a"}</TableCell>
                          <TableCell sx={{ wordBreak: "break-all" }}>{row.error ?? ""}</TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={4}>
                          <Typography color="success.main">No broken links found 🎉</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            {/* Scanned pages list (collapsible) */}
            <Box sx={{ mt: 3 }}>
              <Divider sx={{ mb: 1 }} />
              <Stack direction="row" alignItems="center" spacing={1}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                  Scanned pages ({result.scanned_pages?.length || 0})
                </Typography>
                <Tooltip title={showPages ? "Hide list" : "Show list"}>
                  <IconButton onClick={() => setShowPages((s) => !s)} size="small">
                    {showPages ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Tooltip>
              </Stack>
              <Collapse in={showPages}>
                <Box sx={{ mt: 1, display: "grid", gap: 0.5 }}>
                  {(result.scanned_pages || []).map((p, i) => (
                    <Typography key={i} variant="caption" sx={{ wordBreak: "break-all" }}>
                      {p}
                    </Typography>
                  ))}
                </Box>
              </Collapse>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

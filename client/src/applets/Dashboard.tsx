import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box, CircularProgress, Alert } from '@mui/material';
import ApiService from '../services/ApiService';

interface DashboardProps {
  height?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ height = "80vh" }) => {
  const [summary, setSummary] = useState<any>(null);
  const [geographicData, setGeographicData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const apiService = new ApiService();
        const [summaryResponse, geographicResponse] = await Promise.all([
          apiService.getDashboardSummary(),
          apiService.getGeographicSentiment({ limit: 5 })
        ]);
        
        setSummary(summaryResponse.data);
        setGeographicData(geographicResponse.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height={200}
        flexDirection="column"
        gap={2}
      >
        <CircularProgress color="primary" />
        <Typography variant="body2" color="text.secondary">
          Loading dashboard data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  // Helper function to render sentiment bar
  const renderSentimentBar = (positive: number, negative: number, neutral: number) => {
    const total = positive + negative + neutral;
    if (total === 0) return null;
    
    const positivePercent = (positive / total) * 100;
    const negativePercent = (negative / total) * 100;
    const neutralPercent = (neutral / total) * 100;
    
    return (
      <Box 
        sx={{
          height: 20,
          backgroundColor: '#f0f0f0',
          borderRadius: 2,
          overflow: 'hidden',
          mb: 1,
          display: 'flex'
        }}
      >
        <Box 
          sx={{ 
            backgroundColor: '#4caf50', 
            width: `${positivePercent}%` 
          }} 
        />
        <Box 
          sx={{ 
            backgroundColor: '#f44336', 
            width: `${negativePercent}%` 
          }} 
        />
        <Box 
          sx={{ 
            backgroundColor: '#ff9800', 
            width: `${neutralPercent}%` 
          }} 
        />
      </Box>
    );
  };

  return (
    <Box sx={{ height, overflow: 'auto' }}>
      <Grid container spacing={3}>
        {/* Summary Statistics */}
        <Grid item xs={12} md={6}>
          <Card 
            sx={{ 
              minHeight: 200, 
              borderRadius: 3,
              boxShadow: 2,
              '&:hover': { boxShadow: 4 }
            }}
          >
            <CardContent>
              <Typography 
                variant="h6" 
                component="h2" 
                gutterBottom
                sx={{ 
                  fontWeight: 600,
                  color: 'primary.main'
                }}
              >
                Analytics Summary
              </Typography>
              
              {summary ? (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box textAlign="center" mb={2}>
                      <Typography 
                        variant="h3" 
                        sx={{ 
                          fontWeight: 600,
                          color: 'primary.main'
                        }}
                      >
                        {summary.total_posts || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Posts
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box textAlign="center" mb={2}>
                      <Typography 
                        variant="h3" 
                        sx={{ 
                          fontWeight: 600,
                          color: 'primary.main'
                        }}
                      >
                        {summary.active_sources || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Sources
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" gutterBottom>
                      Sentiment Distribution
                    </Typography>
                    {renderSentimentBar(
                      summary.sentiment?.positive || 0,
                      summary.sentiment?.negative || 0,
                      summary.sentiment?.neutral || 0
                    )}
                    <Box display="flex" justifyContent="space-between" fontSize="small">
                      <Typography variant="caption" color="success.main">
                        Positive: {summary.sentiment?.positive || 0}
                      </Typography>
                      <Typography variant="caption" color="error.main">
                        Negative: {summary.sentiment?.negative || 0}
                      </Typography>
                      <Typography variant="caption" color="warning.main">
                        Neutral: {summary.sentiment?.neutral || 0}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              ) : (
                <Typography color="text.secondary">No summary data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Geographic Data */}
        <Grid item xs={12} md={6}>
          <Card 
            sx={{ 
              minHeight: 200,
              borderRadius: 3,
              boxShadow: 2,
              '&:hover': { boxShadow: 4 }
            }}
          >
            <CardContent>
              <Typography 
                variant="h6" 
                component="h2" 
                gutterBottom
                sx={{ 
                  fontWeight: 600,
                  color: 'primary.main'
                }}
              >
                Top Regions by Activity
              </Typography>
              
              {geographicData && geographicData.length > 0 ? (
                <Box>
                  {geographicData.slice(0, 5).map((region: any, index: number) => (
                    <Box 
                      key={index}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        py: 1,
                        px: 1,
                        borderBottom: index < 4 ? '1px solid' : 'none',
                        borderColor: 'divider',
                      }}
                    >
                      <Typography variant="body2">
                        {region.location || 'Unknown'}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        fontWeight={500}
                        color="primary.main"
                      >
                        {region.count || 0}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary">No geographic data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Box,
  CircularProgress,
  Alert,
  Typography,
  Chip,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
  Fab,
  useTheme
} from '@mui/material';
import {
  RefreshOutlined,
  LocationOnOutlined,
  TimelineOutlined,
  AutoAwesomeOutlined
} from '@mui/icons-material';
import ApiService from '../services/ApiService';
import DashboardCard from '../components/dashboard/DashboardCard';
import MetricsWidget from '../components/dashboard/MetricsWidget';
import SentimentHeatMap from '../components/dashboard/SentimentHeatMap';
import ChartComponent from '../components/dashboard/ChartComponent';

interface DashboardProps {
  height?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ height = "80vh" }) => {
  const theme = useTheme();
  
  const [summary, setSummary] = useState<any>(null);
  const [heatMapData, setHeatMapData] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState('7d');
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    const fetchData = async (showLoading = true) => {
      try {
        if (showLoading) setLoading(true);
        const apiService = new ApiService();
        
        const [summaryResponse, heatMapResponse, analyticsResponse] = await Promise.all([
          apiService.getDashboardSummary(),
          apiService.getSentimentHeatMap({ timeframe }),
          apiService.getAdvancedAnalytics()
        ]);
        
        setSummary(summaryResponse.data);
        setHeatMapData(heatMapResponse.data);
        setAnalytics(analyticsResponse.data);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => fetchData(false), 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [timeframe]);

  const handleRefresh = () => {
    const fetchData = async (showLoading = true) => {
      try {
        if (showLoading) setLoading(true);
        const apiService = new ApiService();
        
        const [summaryResponse, heatMapResponse, analyticsResponse] = await Promise.all([
          apiService.getDashboardSummary(),
          apiService.getSentimentHeatMap({ timeframe }),
          apiService.getAdvancedAnalytics()
        ]);
        
        setSummary(summaryResponse.data);
        setHeatMapData(heatMapResponse.data);
        setAnalytics(analyticsResponse.data);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  };

  const handleTimeframeChange = (event: React.MouseEvent<HTMLElement>, newTimeframe: string) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };

  if (loading && !summary) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height={300}
        flexDirection="column"
        gap={3}
      >
        <CircularProgress size={60} color="primary" />
        <Typography variant="h6" color="text.secondary">
          Loading Analytics Dashboard...
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Analyzing sentiment data and generating insights
        </Typography>
      </Box>
    );
  }

  if (error && !summary) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          action={
            <IconButton color="inherit" size="small" onClick={handleRefresh}>
              <RefreshOutlined />
            </IconButton>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  // Prepare chart data
  const sentimentTrendsData = analytics?.sentiment_trends?.map((item: any) => ({
    date: item.date,
    positive: item.positive,
    negative: item.negative,
    neutral: item.neutral
  })) || [];

  const platformData = analytics?.platform_performance?.map((item: any) => ({
    name: item.platform,
    posts: item.posts,
    sentiment: (item.avg_sentiment * 100).toFixed(1)
  })) || [];

  const metricsData = [
    { label: 'Total Posts', value: summary?.total_posts || 0, trend: 'up' as const, change: 12.5 },
    { label: 'Active Sources', value: summary?.active_sources || 0, trend: 'up' as const, change: 8.2 },
    { label: 'Avg Confidence', value: analytics?.performance_metrics?.cache_hit_rate || 0, format: 'percentage' as const, trend: 'up' as const, change: 5.1 },
    { label: 'Response Time', value: analytics?.performance_metrics?.avg_processing_time || 0, format: 'time' as const, trend: 'down' as const, change: -3.2 }
  ];

  return (
    <Box sx={{ height, overflow: 'auto' }}>
      {/* Header */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main}15 0%, ${theme.palette.secondary.main}15 100%)`,
          borderRadius: 3,
          p: 3
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight={700} color="primary.main" gutterBottom>
            Analytics Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time sentiment analysis and insights
          </Typography>
          <Chip
            icon={<AutoAwesomeOutlined />}
            label={`Last updated: ${lastUpdated.toLocaleTimeString()}`}
            size="small"
            sx={{ mt: 1 }}
          />
        </Box>

        <Box display="flex" alignItems="center" gap={2}>
          <ToggleButtonGroup
            value={timeframe}
            exclusive
            onChange={handleTimeframeChange}
            size="small"
          >
            <ToggleButton value="1d">1D</ToggleButton>
            <ToggleButton value="7d">7D</ToggleButton>
            <ToggleButton value="30d">30D</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} lg={3}>
          <DashboardCard
            title="Key Metrics"
            tooltip="Overview of core platform metrics"
            height={400}
          >
            <MetricsWidget metrics={metricsData} />
          </DashboardCard>
        </Grid>

        {/* Sentiment Trends Chart */}
        <Grid item xs={12} lg={6}>
          <DashboardCard
            title="Sentiment Trends"
            tooltip="Daily sentiment analysis over time"
            height={400}
          >
            <ChartComponent
              type="line"
              data={sentimentTrendsData}
              xAxisKey="date"
              yAxisKeys={['positive', 'negative', 'neutral']}
              height={320}
              colors={[theme.palette.success.main, theme.palette.error.main, theme.palette.warning.main]}
            />
          </DashboardCard>
        </Grid>

        {/* Platform Performance */}
        <Grid item xs={12} lg={3}>
          <DashboardCard
            title="Platform Performance"
            tooltip="Post volume and sentiment by platform"
            height={400}
          >
            <ChartComponent
              type="bar"
              data={platformData}
              xAxisKey="name"
              yAxisKeys={['posts']}
              height={320}
              showLegend={false}
            />
          </DashboardCard>
        </Grid>

        {/* Sentiment Heat Map */}
        <Grid item xs={12} lg={8}>
          <DashboardCard
            title="Topic Sentiment Heat Map"
            tooltip="Sentiment intensity across topics and time"
            height={450}
            action={
              <Chip
                icon={<TimelineOutlined />}
                label={`${timeframe.toUpperCase()} View`}
                size="small"
                color="primary"
              />
            }
          >
            <SentimentHeatMap
              data={heatMapData?.heat_map_data || []}
              timeframe={timeframe}
            />
          </DashboardCard>
        </Grid>

        {/* Geographic Distribution */}
        <Grid item xs={12} lg={4}>
          <DashboardCard
            title="Geographic Activity"
            tooltip="Top regions by post volume"
            height={450}
          >
            <Box sx={{ p: 1 }}>
              {summary?.top_regions?.map((region: any, index: number) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 2,
                    px: 2,
                    mb: 1,
                    borderRadius: 2,
                    backgroundColor: 'action.hover',
                    '&:hover': {
                      backgroundColor: 'action.selected',
                      transform: 'scale(1.02)'
                    },
                    transition: 'all 0.2s ease'
                  }}
                >
                  <Box display="flex" alignItems="center" gap={1}>
                    <LocationOnOutlined fontSize="small" color="primary" />
                    <Typography variant="body2" fontWeight={500}>
                      {region.location}
                    </Typography>
                  </Box>
                  <Chip
                    label={region.post_count}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              ))}
            </Box>
          </DashboardCard>
        </Grid>

        {/* Trending Topics */}
        <Grid item xs={12} lg={6}>
          <DashboardCard
            title="Trending Topics"
            tooltip="Most mentioned topics with sentiment scores"
            height={300}
          >
            <Box sx={{ p: 1 }}>
              {summary?.trending_topics?.slice(0, 5).map((topic: any, index: number) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 1.5,
                    px: 2,
                    mb: 1,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    '&:hover': {
                      borderColor: 'primary.main',
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                      '& .MuiChip-root': {
                        backgroundColor: 'rgba(255,255,255,0.2)',
                        color: 'inherit'
                      }
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  <Box>
                    <Typography variant="body2" fontWeight={600}>
                      #{topic.topic}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {topic.mentions} mentions
                    </Typography>
                  </Box>
                  <Chip
                    label={`${(topic.sentiment_score * 100).toFixed(0)}%`}
                    size="small"
                    color={topic.sentiment_score > 0.5 ? 'success' : 'warning'}
                  />
                </Box>
              ))}
            </Box>
          </DashboardCard>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} lg={6}>
          <DashboardCard
            title="Recent Activity"
            tooltip="Latest platform events and updates"
            height={300}
          >
            <Box sx={{ p: 1 }}>
              {summary?.recent_activity?.map((activity: any, index: number) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    py: 1.5,
                    px: 2,
                    mb: 1,
                    borderRadius: 2,
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: 'primary.main'
                    }}
                  />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" fontWeight={500}>
                      {activity.event}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(activity.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </DashboardCard>
        </Grid>
      </Grid>

      {/* Floating Action Button for Manual Refresh */}
      <Fab
        color="primary"
        aria-label="refresh"
        onClick={handleRefresh}
        disabled={loading}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000
        }}
      >
        <RefreshOutlined />
      </Fab>
    </Box>
  );
};

export default Dashboard;
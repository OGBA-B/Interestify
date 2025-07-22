import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box, CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import ApiService from '../services/ApiService';

const useStyles = makeStyles((theme) => ({
  card: {
    minHeight: 200,
    margin: theme.spacing(1),
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: theme.spacing(2),
  },
  stat: {
    textAlign: 'center',
    marginBottom: theme.spacing(2),
  },
  statNumber: {
    fontSize: 36,
    fontWeight: 'bold',
    color: theme.palette.primary.main,
  },
  statLabel: {
    fontSize: 14,
    color: theme.palette.text.secondary,
  },
  sentimentBar: {
    height: 20,
    backgroundColor: '#f0f0f0',
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: theme.spacing(1),
  },
  sentimentSegment: {
    height: '100%',
    display: 'inline-block',
  },
  positive: {
    backgroundColor: '#4caf50',
  },
  negative: {
    backgroundColor: '#f44336',
  },
  neutral: {
    backgroundColor: '#ff9800',
  },
  regionItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing(1),
    borderBottom: '1px solid #eee',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: 200,
  },
}));

interface DashboardProps {
  height?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ height = "80vh" }) => {
  const classes = useStyles();
  const [summary, setSummary] = useState<any>(null);
  const [geographicData, setGeographicData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const apiService = new ApiService(); // Create inside useEffect
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
  }, []); // Empty dependency array

  if (loading) {
    return (
      <Box className={classes.loading}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box className={classes.loading}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  const renderSentimentBar = (distribution: any) => {
    const total = distribution.positive + distribution.negative + distribution.neutral;
    if (total === 0) return null;

    const positivePercent = (distribution.positive / total) * 100;
    const negativePercent = (distribution.negative / total) * 100;
    const neutralPercent = (distribution.neutral / total) * 100;

    return (
      <div className={classes.sentimentBar}>
        <div 
          className={`${classes.sentimentSegment} ${classes.positive}`}
          style={{ width: `${positivePercent}%` }}
        />
        <div 
          className={`${classes.sentimentSegment} ${classes.negative}`}
          style={{ width: `${negativePercent}%` }}
        />
        <div 
          className={`${classes.sentimentSegment} ${classes.neutral}`}
          style={{ width: `${neutralPercent}%` }}
        />
      </div>
    );
  };

  return (
    <Box style={{ height, overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Geographic Interest Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Summary Statistics */}
        <Grid item xs={12} md={4}>
          <Card className={classes.card}>
            <CardContent>
              <Typography className={classes.cardTitle}>
                Summary Statistics
              </Typography>
              
              <div className={classes.stat}>
                <div className={classes.statNumber}>
                  {summary?.total_posts_with_location || 0}
                </div>
                <div className={classes.statLabel}>
                  Posts with Location
                </div>
              </div>
              
              <div className={classes.stat}>
                <div className={classes.statNumber}>
                  {summary?.total_unique_locations || 0}
                </div>
                <div className={classes.statLabel}>
                  Unique Locations
                </div>
              </div>

              {summary?.note && (
                <Typography variant="caption" color="textSecondary">
                  {summary.note}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Overall Sentiment Distribution */}
        <Grid item xs={12} md={4}>
          <Card className={classes.card}>
            <CardContent>
              <Typography className={classes.cardTitle}>
                Overall Sentiment
              </Typography>
              
              {summary?.overall_sentiment_distribution && (
                <>
                  {renderSentimentBar(summary.overall_sentiment_distribution)}
                  
                  <Box mt={2}>
                    <Typography variant="body2">
                      <span style={{ color: '#4caf50' }}>●</span> Positive: {summary.overall_sentiment_distribution.positive}
                    </Typography>
                    <Typography variant="body2">
                      <span style={{ color: '#f44336' }}>●</span> Negative: {summary.overall_sentiment_distribution.negative}
                    </Typography>
                    <Typography variant="body2">
                      <span style={{ color: '#ff9800' }}>●</span> Neutral: {summary.overall_sentiment_distribution.neutral}
                    </Typography>
                  </Box>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top Regions */}
        <Grid item xs={12} md={4}>
          <Card className={classes.card}>
            <CardContent>
              <Typography className={classes.cardTitle}>
                Top Regions
              </Typography>
              
              {summary?.top_regions?.map((region: any, index: number) => (
                <div key={index} className={classes.regionItem}>
                  <Typography variant="body2">
                    {region.location}
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {region.post_count} posts
                  </Typography>
                </div>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Geographic Sentiment Details */}
        <Grid item xs={12}>
          <Card className={classes.card}>
            <CardContent>
              <Typography className={classes.cardTitle}>
                Geographic Sentiment Analysis
              </Typography>
              
              <Grid container spacing={2}>
                {geographicData?.geographic_data?.map((location: any, index: number) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {location.location}
                        </Typography>
                        
                        <Typography variant="body2" color="textSecondary">
                          {location.total_posts} posts • {(location.average_confidence * 100).toFixed(1)}% confidence
                        </Typography>
                        
                        <Box mt={2}>
                          {renderSentimentBar(location.sentiment_distribution)}
                        </Box>
                        
                        <Box mt={1}>
                          <Typography variant="caption">
                            Positive: {location.sentiment_distribution.positive} • 
                            Negative: {location.sentiment_distribution.negative} • 
                            Neutral: {location.sentiment_distribution.neutral}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {geographicData?.note && (
                <Box mt={2}>
                  <Typography variant="caption" color="textSecondary">
                    {geographicData.note}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
import React from 'react';
import { Box, Typography, Tooltip, useTheme } from '@mui/material';

interface HeatMapData {
  topic: string;
  time_series: Array<{
    timestamp: string;
    positive: number;
    negative: number;
    neutral: number;
    sentiment_score: number;
  }>;
}

interface SentimentHeatMapProps {
  data: HeatMapData[];
  timeframe: string;
}

const SentimentHeatMap: React.FC<SentimentHeatMapProps> = ({ data, timeframe }) => {
  const theme = useTheme();

  const getColorFromSentiment = (score: number) => {
    // Normalize score to 0-1 range (score is typically between -1 and 1)
    const normalizedScore = (score + 1) / 2;
    
    if (normalizedScore > 0.7) {
      return theme.palette.success.main;
    } else if (normalizedScore > 0.5) {
      return theme.palette.success.light;
    } else if (normalizedScore > 0.3) {
      return theme.palette.warning.light;
    } else {
      return theme.palette.error.main;
    }
  };

  const getIntensity = (score: number) => {
    const normalizedScore = Math.abs(score);
    return Math.min(normalizedScore * 0.8 + 0.2, 1);
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    if (timeframe === '1d') {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  if (!data || data.length === 0) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height={200}
      >
        <Typography color="text.secondary">No heat map data available</Typography>
      </Box>
    );
  }

  const timePoints = data[0]?.time_series || [];

  return (
    <Box sx={{ p: 2 }}>
      {/* Legend */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="body2" color="text.secondary">
          Topics
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="caption" color="text.secondary">Negative</Typography>
          <Box
            sx={{
              width: 60,
              height: 8,
              background: `linear-gradient(to right, ${theme.palette.error.main}, ${theme.palette.warning.light}, ${theme.palette.success.light}, ${theme.palette.success.main})`,
              borderRadius: 1
            }}
          />
          <Typography variant="caption" color="text.secondary">Positive</Typography>
        </Box>
      </Box>

      {/* Heat Map Grid */}
      <Box sx={{ overflowX: 'auto' }}>
        <Box sx={{ minWidth: 400 }}>
          {/* Time Headers */}
          <Box display="flex" mb={1}>
            <Box sx={{ width: 120, flexShrink: 0 }} /> {/* Topic label space */}
            {timePoints.map((point, index) => (
              <Box
                key={index}
                sx={{
                  flex: 1,
                  minWidth: 40,
                  textAlign: 'center',
                  px: 0.5
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  {formatDate(point.timestamp)}
                </Typography>
              </Box>
            ))}
          </Box>

          {/* Heat Map Rows */}
          {data.map((topicData, topicIndex) => (
            <Box key={topicIndex} display="flex" alignItems="center" mb={1}>
              {/* Topic Label */}
              <Box
                sx={{
                  width: 120,
                  flexShrink: 0,
                  pr: 2
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontSize: '0.8rem',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {topicData.topic}
                </Typography>
              </Box>

              {/* Heat Map Cells */}
              {topicData.time_series.map((point, timeIndex) => (
                <Tooltip
                  key={timeIndex}
                  title={
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        {topicData.topic}
                      </Typography>
                      <Typography variant="caption">
                        {formatDate(point.timestamp)}
                      </Typography>
                      <br />
                      <Typography variant="caption" color="success.main">
                        Positive: {point.positive}
                      </Typography>
                      <br />
                      <Typography variant="caption" color="error.main">
                        Negative: {point.negative}
                      </Typography>
                      <br />
                      <Typography variant="caption" color="warning.main">
                        Neutral: {point.neutral}
                      </Typography>
                      <br />
                      <Typography variant="caption">
                        Sentiment Score: {point.sentiment_score.toFixed(2)}
                      </Typography>
                    </Box>
                  }
                  arrow
                >
                  <Box
                    sx={{
                      flex: 1,
                      minWidth: 40,
                      height: 24,
                      mx: 0.25,
                      borderRadius: 1,
                      backgroundColor: getColorFromSentiment(point.sentiment_score),
                      opacity: getIntensity(point.sentiment_score),
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        opacity: 1,
                        transform: 'scale(1.1)',
                        zIndex: 1
                      }
                    }}
                  />
                </Tooltip>
              ))}
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default SentimentHeatMap;
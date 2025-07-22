import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

interface MetricItem {
  label: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'flat';
  format?: 'number' | 'percentage' | 'currency' | 'time';
}

interface MetricsWidgetProps {
  metrics: MetricItem[];
}

const MetricsWidget: React.FC<MetricsWidgetProps> = ({ metrics }) => {
  const formatValue = (value: string | number, format: MetricItem['format'] = 'number') => {
    if (typeof value === 'string') return value;
    
    switch (format) {
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'currency':
        return `$${value.toFixed(2)}`;
      case 'time':
        return `${value.toFixed(1)}s`;
      default:
        return value.toLocaleString();
    }
  };

  const getTrendIcon = (trend: MetricItem['trend']) => {
    switch (trend) {
      case 'up':
        return <TrendingUp fontSize="small" color="success" />;
      case 'down':
        return <TrendingDown fontSize="small" color="error" />;
      case 'flat':
        return <TrendingFlat fontSize="small" color="disabled" />;
      default:
        return null;
    }
  };

  const getTrendColor = (trend: MetricItem['trend'], change?: number) => {
    if (!change) return 'default';
    if (trend === 'up') return 'success';
    if (trend === 'down') return 'error';
    return 'default';
  };

  return (
    <Box>
      {metrics.map((metric, index) => (
        <Box
          key={index}
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            py: 2,
            px: 1,
            borderBottom: index < metrics.length - 1 ? '1px solid' : 'none',
            borderColor: 'divider',
            '&:hover': {
              backgroundColor: 'action.hover',
              borderRadius: 1
            }
          }}
        >
          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontSize: '0.875rem' }}
            >
              {metric.label}
            </Typography>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: 'text.primary',
                fontSize: '1.25rem'
              }}
            >
              {formatValue(metric.value, metric.format)}
            </Typography>
          </Box>
          
          {(metric.change !== undefined || metric.trend) && (
            <Box display="flex" alignItems="center" gap={1}>
              {metric.trend && getTrendIcon(metric.trend)}
              {metric.change !== undefined && (
                <Chip
                  label={`${metric.change > 0 ? '+' : ''}${metric.change.toFixed(1)}%`}
                  size="small"
                  color={getTrendColor(metric.trend, metric.change)}
                  variant="outlined"
                  sx={{
                    fontSize: '0.75rem',
                    height: 24
                  }}
                />
              )}
            </Box>
          )}
        </Box>
      ))}
    </Box>
  );
};

export default MetricsWidget;
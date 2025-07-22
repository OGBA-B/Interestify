import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Box, useTheme } from '@mui/material';

interface ChartData {
  name?: string;
  date?: string;
  [key: string]: any;
}

interface ChartComponentProps {
  type: 'line' | 'bar' | 'pie';
  data: ChartData[];
  xAxisKey: string;
  yAxisKeys?: string[];
  colors?: string[];
  height?: number;
  showGrid?: boolean;
  showLegend?: boolean;
}

const ChartComponent: React.FC<ChartComponentProps> = ({
  type,
  data,
  xAxisKey,
  yAxisKeys = [],
  colors,
  height = 300,
  showGrid = true,
  showLegend = true
}) => {
  const theme = useTheme();

  const defaultColors = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
    theme.palette.info.main
  ];

  const chartColors = colors || defaultColors;

  const formatXAxisLabel = (value: any) => {
    if (xAxisKey === 'date' && typeof value === 'string') {
      const date = new Date(value);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
    return value;
  };

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: 'background.paper',
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            p: 2,
            boxShadow: 2
          }}
        >
          <Box sx={{ mb: 1, fontWeight: 600 }}>
            {xAxisKey === 'date' ? formatXAxisLabel(label) : label}
          </Box>
          {payload.map((item: any, index: number) => (
            <Box key={index} sx={{ color: item.color, fontSize: '0.875rem' }}>
              {`${item.name}: ${item.value}`}
            </Box>
          ))}
        </Box>
      );
    }
    return null;
  };

  const renderChart = () => {
    switch (type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
              <XAxis
                dataKey={xAxisKey}
                tickFormatter={formatXAxisLabel}
                stroke={theme.palette.text.secondary}
                fontSize={12}
              />
              <YAxis stroke={theme.palette.text.secondary} fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              {showLegend && <Legend />}
              {yAxisKeys.map((key, index) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={chartColors[index % chartColors.length]}
                  strokeWidth={2}
                  dot={{ fill: chartColors[index % chartColors.length], strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: chartColors[index % chartColors.length], strokeWidth: 2 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />}
              <XAxis
                dataKey={xAxisKey}
                tickFormatter={formatXAxisLabel}
                stroke={theme.palette.text.secondary}
                fontSize={12}
              />
              <YAxis stroke={theme.palette.text.secondary} fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              {showLegend && <Legend />}
              {yAxisKeys.map((key, index) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={chartColors[index % chartColors.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                outerRadius={Math.min(height * 0.35, 120)}
                fill="#8884d8"
                dataKey={yAxisKeys[0] || 'value'}
                label={({ name, percent }: { name?: string; percent?: number }) => 
                  `${name || 'Unknown'}: ${((percent || 0) * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={chartColors[index % chartColors.length]}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return <Box sx={{ width: '100%', height }}>{renderChart()}</Box>;
};

export default ChartComponent;
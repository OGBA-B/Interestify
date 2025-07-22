import React from 'react';
import { Card, CardContent, Typography, Box, IconButton, Tooltip } from '@mui/material';
import { InfoOutlined } from '@mui/icons-material';

interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
  tooltip?: string;
  action?: React.ReactNode;
  height?: number | string;
  sx?: any;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  children,
  tooltip,
  action,
  height = 'auto',
  sx = {}
}) => {
  return (
    <Card
      sx={{
        height,
        borderRadius: 3,
        boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
          transform: 'translateY(-2px)'
        },
        background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
        border: '1px solid',
        borderColor: 'divider',
        ...sx
      }}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography
              variant="h6"
              component="h2"
              sx={{
                fontWeight: 600,
                color: 'text.primary',
                fontSize: '1.1rem'
              }}
            >
              {title}
            </Typography>
            {tooltip && (
              <Tooltip title={tooltip} arrow>
                <IconButton size="small" sx={{ color: 'text.secondary' }}>
                  <InfoOutlined fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          {action && <Box>{action}</Box>}
        </Box>
        <Box>{children}</Box>
      </CardContent>
    </Card>
  );
};

export default DashboardCard;
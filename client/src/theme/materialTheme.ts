import { createTheme } from '@mui/material/styles';

// Material Design 3 color tokens
const materialColors = {
  primary: {
    main: '#6750A4', // Material Design 3 primary
    light: '#7F67BE',
    dark: '#21005D',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#625B71', // Material Design 3 secondary
    light: '#7C748B',
    dark: '#463D52',
    contrastText: '#FFFFFF',
  },
  tertiary: {
    main: '#7D5260', // Material Design 3 tertiary
    light: '#976B7A',
    dark: '#633B48',
    contrastText: '#FFFFFF',
  },
  error: {
    main: '#BA1A1A',
    light: '#C84848',
    dark: '#93000A',
    contrastText: '#FFFFFF',
  },
  warning: {
    main: '#F59E0B',
    light: '#F7B731',
    dark: '#D97706',
    contrastText: '#FFFFFF',
  },
  info: {
    main: '#2196F3',
    light: '#64B5F6',
    dark: '#1976D2',
    contrastText: '#FFFFFF',
  },
  success: {
    main: '#10B981',
    light: '#34D399',
    dark: '#059669',
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#FFFBFE', // Material Design 3 surface
    paper: '#FFFBFE',
  },
  surface: {
    main: '#FFFBFE',
    variant: '#E7E0EC',
    container: '#F3EDF7',
    containerHighest: '#E6E0E9',
  },
  outline: {
    main: '#79747E',
    variant: '#CAC4D0',
  },
};

// Material Design 3 Typography Scale
const materialTypography = {
  fontFamily: [
    'Roboto',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
  ].join(','),
  // Display Large
  h1: {
    fontSize: '3.5625rem', // 57px
    lineHeight: '4rem', // 64px
    fontWeight: 400,
    letterSpacing: '-0.25px',
  },
  // Display Medium
  h2: {
    fontSize: '2.8125rem', // 45px
    lineHeight: '3.25rem', // 52px
    fontWeight: 400,
    letterSpacing: '0px',
  },
  // Display Small
  h3: {
    fontSize: '2.25rem', // 36px
    lineHeight: '2.75rem', // 44px
    fontWeight: 400,
    letterSpacing: '0px',
  },
  // Headline Large
  h4: {
    fontSize: '2rem', // 32px
    lineHeight: '2.5rem', // 40px
    fontWeight: 400,
    letterSpacing: '0px',
  },
  // Headline Medium
  h5: {
    fontSize: '1.75rem', // 28px
    lineHeight: '2.25rem', // 36px
    fontWeight: 400,
    letterSpacing: '0px',
  },
  // Headline Small
  h6: {
    fontSize: '1.5rem', // 24px
    lineHeight: '2rem', // 32px
    fontWeight: 400,
    letterSpacing: '0px',
  },
  // Title Large
  subtitle1: {
    fontSize: '1.375rem', // 22px
    lineHeight: '1.75rem', // 28px
    fontWeight: 400,
    letterSpacing: '0px',
  },
  // Title Medium
  subtitle2: {
    fontSize: '1rem', // 16px
    lineHeight: '1.5rem', // 24px
    fontWeight: 500,
    letterSpacing: '0.15px',
  },
  // Body Large
  body1: {
    fontSize: '1rem', // 16px
    lineHeight: '1.5rem', // 24px
    fontWeight: 400,
    letterSpacing: '0.5px',
  },
  // Body Medium
  body2: {
    fontSize: '0.875rem', // 14px
    lineHeight: '1.25rem', // 20px
    fontWeight: 400,
    letterSpacing: '0.25px',
  },
  // Label Large
  button: {
    fontSize: '0.875rem', // 14px
    lineHeight: '1.25rem', // 20px
    fontWeight: 500,
    letterSpacing: '0.1px',
    textTransform: 'none' as const,
  },
  // Label Medium
  caption: {
    fontSize: '0.75rem', // 12px
    lineHeight: '1rem', // 16px
    fontWeight: 500,
    letterSpacing: '0.5px',
  },
  // Label Small
  overline: {
    fontSize: '0.6875rem', // 11px
    lineHeight: '1rem', // 16px
    fontWeight: 500,
    letterSpacing: '0.5px',
    textTransform: 'uppercase' as const,
  },
};

// Material Design 3 Elevation
const elevations = [
  'none',
  '0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
  '0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15)',
  '0px 1px 3px 0px rgba(0, 0, 0, 0.3), 0px 4px 8px 3px rgba(0, 0, 0, 0.15)',
  '0px 2px 3px 0px rgba(0, 0, 0, 0.3), 0px 6px 10px 4px rgba(0, 0, 0, 0.15)',
  '0px 4px 4px 0px rgba(0, 0, 0, 0.3), 0px 8px 12px 6px rgba(0, 0, 0, 0.15)',
];

const materialTheme = createTheme({
  palette: {
    mode: 'light',
    primary: materialColors.primary,
    secondary: materialColors.secondary,
    error: materialColors.error,
    warning: materialColors.warning,
    info: materialColors.info,
    success: materialColors.success,
    background: materialColors.background,
    text: {
      primary: '#1C1B1F',
      secondary: '#49454F',
      disabled: '#1C1B1F61',
    },
  },
  typography: materialTypography,
  shape: {
    borderRadius: 12, // Material Design 3 uses more rounded corners
  },
  spacing: 8, // 8px base spacing unit
  shadows: elevations as any,
  components: {
    // Material Design 3 Button styling
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 20, // Pill-shaped buttons
          textTransform: 'none',
          fontWeight: 500,
          padding: '10px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
          },
        },
        contained: {
          background: materialColors.primary.main,
          '&:hover': {
            background: materialColors.primary.dark,
          },
        },
        outlined: {
          borderColor: materialColors.outline.main,
          color: materialColors.primary.main,
          '&:hover': {
            borderColor: materialColors.primary.main,
            backgroundColor: `${materialColors.primary.main}08`,
          },
        },
      },
    },
    // Material Design 3 Card styling
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: elevations[1],
          backgroundColor: materialColors.surface.container,
          '&:hover': {
            boxShadow: elevations[2],
          },
        },
      },
    },
    // Material Design 3 TextField styling
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 4,
            '& fieldset': {
              borderColor: materialColors.outline.main,
            },
            '&:hover fieldset': {
              borderColor: materialColors.primary.main,
            },
            '&.Mui-focused fieldset': {
              borderColor: materialColors.primary.main,
              borderWidth: 2,
            },
          },
        },
      },
    },
    // Material Design 3 AppBar styling
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: materialColors.surface.container,
          color: materialColors.primary.main,
          boxShadow: 'none',
          borderBottom: `1px solid ${materialColors.outline.variant}`,
        },
      },
    },
    // Material Design 3 Paper styling
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: materialColors.surface.container,
          borderRadius: 12,
        },
      },
    },
    // Table styling for Material Design 3
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: materialColors.surface.containerHighest,
          '& .MuiTableCell-head': {
            color: materialColors.primary.main,
            fontWeight: 500,
            borderBottom: `2px solid ${materialColors.primary.main}`,
          },
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: `${materialColors.primary.main}08`,
          },
          '&:nth-of-type(odd)': {
            backgroundColor: materialColors.surface.main,
          },
          '&:nth-of-type(even)': {
            backgroundColor: materialColors.surface.variant,
          },
        },
      },
    },
  },
});

export default materialTheme;
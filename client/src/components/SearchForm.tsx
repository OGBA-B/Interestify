import React from 'react';
import { Button, TextField, Box, Stack } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface SearchFormProps {
    dispatch: Function,
    searchKey: string
}

const SearchForm = (props: SearchFormProps): JSX.Element => {
    const { searchKey, dispatch } = props;

    /**
     * handles changes to the input text field
     * @param $event event object
     */
    const handleSearchChange = ($event: React.ChangeEvent<HTMLInputElement>): void => {
        dispatch({ type: 'typing', payload: { searchKey: $event.target.value } });
    }

    return (
        <Box component="form" onSubmit={($event: React.FormEvent<HTMLFormElement>) => {
            $event.preventDefault();
            dispatch({ type: 'startSearch', payload: { query: searchKey } });
        }}>
            <Stack direction="row" spacing={2} alignItems="center">
                <TextField 
                    autoFocus 
                    size="medium" 
                    type="text" 
                    variant="filled" 
                    value={searchKey} 
                    onChange={handleSearchChange}
                    placeholder="search" 
                    fullWidth
                    sx={{ 
                        flexGrow: 1,
                        '& .MuiFilledInput-root': {
                            '&:hover': {
                                backgroundColor: 'rgba(103, 80, 164, 0.08)',
                            },
                            '&.Mui-focused': {
                                backgroundColor: 'rgba(103, 80, 164, 0.08)',
                            },
                        },
                    }}
                />
                <Button 
                    type="submit" 
                    variant="contained" 
                    color="primary"
                    startIcon={<SearchIcon />}
                    sx={{ 
                        borderRadius: 20, // Increased for softer pill shape
                        px: 4, // Increased padding
                        py: 2, // Increased padding
                        minHeight: 48, // Better touch target
                        boxShadow: '0px 2px 4px 0px rgba(103, 80, 164, 0.24)',
                        '&:hover': {
                            boxShadow: '0px 4px 8px 0px rgba(103, 80, 164, 0.32)',
                            transform: 'translateY(-1px)', // Subtle lift effect
                        },
                        transition: 'all 0.2s ease-in-out', // Smooth transitions
                    }}
                >
                    Search
                </Button>
            </Stack>
        </Box>
    );
}

export default SearchForm;
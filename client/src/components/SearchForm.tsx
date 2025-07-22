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
                    size="small" 
                    type="text" 
                    variant="outlined" 
                    value={searchKey} 
                    onChange={handleSearchChange}
                    placeholder="search" 
                    fullWidth
                    sx={{ flexGrow: 1 }}
                />
                <Button 
                    type="submit" 
                    variant="contained" 
                    color="primary"
                    startIcon={<SearchIcon />}
                    sx={{ 
                        borderRadius: 5,
                        px: 3,
                        py: 1.5,
                    }}
                >
                    Search
                </Button>
            </Stack>
        </Box>
    );
}

export default SearchForm;
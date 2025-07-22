import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
 
interface PanelProps {
    children: React.ReactNode,
    width?: string,
    height?: string,
    id?: string,
    overflow?: string,
    title?: string
}

const Panel = (props: PanelProps): JSX.Element => {
    const style = {
        width: props.width || undefined,
        height: props.height || undefined,
        overflow: props.overflow,
    };

    return (
        <Card 
            id={props.id} 
            sx={{
                ...style,
                borderRadius: 3,
                boxShadow: 2,
                '&:hover': {
                    boxShadow: 3,
                },
            }}
        >
            <CardContent sx={{ p: 3 }}>
                {props.title && (
                    <Typography variant="h6" component="h2" gutterBottom>
                        {props.title}
                    </Typography>
                )}
                <Box>
                    {props.children}
                </Box>
            </CardContent>
        </Card>
    );
}

export default Panel;
import React, { useContext, useReducer, useEffect } from 'react';
import { Table, TableHead, TableRow, TableCell, TableBody, IconButton, TableSortLabel, TableFooter, TablePagination } from '@material-ui/core';
import { AddCircle, Delete } from '@material-ui/icons';
import LastPageIcon from '@material-ui/icons/LastPage';
import FirstPageIcon from '@material-ui/icons/FirstPage';
import KeyboardArrowLeft from '@material-ui/icons/KeyboardArrowLeft';
import KeyboardArrowRight from '@material-ui/icons/KeyboardArrowRight';
import * as _ from 'lodash';

export interface TableHeader {
	id: string,
	title: string
}

type DataRow = Record<string, any>;

interface TableProps {
        header: TableHeader[],
        body: DataRow[],
	striped?: boolean,
	pagination?: PaginationOptions,
	actions?: boolean,
	sortable?: boolean,
	missingValue?: string,
	footer?: JSX.Element,
	elevated?: boolean,
	sort?: SortBy
}

interface HeaderProps {
    sortable?: boolean
}

interface BodyProps {
    striped?: boolean,
    actions?: boolean,
    missingValue?: string
}

interface TableState {
        headerData: TableHeader[],
        bodyData: DataRow[],
	footerData: JSX.Element | undefined,
	sortBy: SortBy,
	pagination: PaginationState | undefined
}

interface SortBy {
	id: string,
	order: 'asc' | 'desc'
}

interface PaginationOptions {
	rowsPerPageOptions: number[],
	colSpan?: number,
	rowsPerPage: number,
	currentPage?: number,
}

interface PaginationState {
	currentPageIndex: number,
	rowsPerPage: number
}

interface ReducerAction {
    type: string,
    payload: any
}

const ActionIcons: {[index: string]: any} = {
	add: <AddCircle fontSize='small' />,
	delete: <Delete fontSize='small' />
}

/**
 * sorts a collection
 * @author oderah
 * 
 * @param collection collection to be sorted
 * @param id key to sort collection by
 * @param order order to sort collection
 * 
 * @return the sorted collection
 */
const sortCollectionBy = (collection: DataRow[], id: string, order: 'asc' | 'desc'): DataRow[] => {
    var sorted = [ ...collection ];
    sorted = _.orderBy(sorted, id, order);
    return sorted
}

/**
 * handles state changes based on the specified action
 * @uthor oderah
 * 
 * @param state current state of the table
 * @param action action to be performed
 */
const tableReducer = (state: TableState, action: ReducerAction): TableState => {
    const { type, payload } = action;

    switch (type) {
        case 'sort':
            let sortBy: SortBy = {
                id: payload.sortBy.id,
                order: (payload.sortBy.order) ? payload.sortBy.order : (state.sortBy.id === action.payload.sortBy.id) ? ((state.sortBy.order === 'asc') ? 'desc' : 'asc') : 'asc'
            }
            return {
                ...state,
                sortBy: {
                    id: sortBy.id,
                    order: sortBy.order
                },
                bodyData: sortCollectionBy(state.bodyData, sortBy.id, sortBy.order),
            };

        case 'initialSort':
            return {
                ...state,
                bodyData: sortCollectionBy(state.bodyData, state.sortBy.id, state.sortBy.order)
            }
        
        case 'updatePagination':
            return {
                ...state,
                pagination: {
                    currentPageIndex: payload.currentPageIndex,
                    rowsPerPage: payload.rowsPerPage
                }
            };
        
        default:
            return state;
    }

}

/**
 * orders a row object in the same order as state.headerData
 * @author oderah
 * 
 * @param row an object containing info for a table row
 * @param header data from header
 * @param hasActions determines if the actions column should be displayed
 * @param missingValue specified to string used to represnt missing values
 * 
 * @return an array containg the data of the row object
 * 			in an ordered format.
 */
const orderByHeader = (row: DataRow, header: TableHeader[], hasActions: boolean, missingValue?: string): any[] => {
    var entries = Object.entries(row);
    var rowData: any[] = [];
    header.forEach(heading => {
        var entry: any = entries.find(x => x[0] === heading.id);
        if (entry) { // if entry is found
            if (hasActions && 'actions' === heading.id) { // if actions
                // map icons for all actions
                var actions = entry[1].map((action: any, index: number) => 
                    <IconButton 
                        key={ index } 
                        children={ ActionIcons[action.icon] }
                        size='small'
                        onClick={ action.click } />);
                rowData.push(actions); 
            } else { // if other properties other than actions
                rowData.push(entry[1]);
            }
        } else {
            rowData.push((missingValue) ? missingValue : <span>&mdash;</span>);
        }
    });
    return rowData;
}

const InterestifyTable = (props: TableProps) => {
    
    /**
	 * creates the header of the table
	 * @author oderah
	 * 
	 * @return a TableHead component which has a TableRow component containing info 
	 * 			from state.headerData mapped to a TableCell component
	 */
    const Header = (props: HeaderProps): JSX.Element => {
        const state = useContext(StateContext);
        const  dispatch = useContext(DispatchContext);
        
        return (
            <TableHead className={ (elevated) ? 'elevated-table' : '' }>
                <TableRow children={ state.headerData.map((column: any) => 
                <TableCell key={ column.id }>{ (props.sortable && 'actions' !== column.id) ? 
                                                    <TableSortLabel 
                                                        active={ column.id === state.sortBy.id } 
                                                        direction={ (state.sortBy.id === column.id) ? state.sortBy.order : 'asc' } 
                                                        children={ column.title } 
                                                        onClick={ ($event: any) => 
                                                            { dispatch({ 
                                                                type: 'sort', 
                                                                payload: { 
                                                                    sortBy: { 
                                                                        id: column.id 
                                                                    } 
                                                                } 
                                                                }) } } /> : column.title } </TableCell>) } />
            </TableHead>
        );
    }
    
    /**
	 * creates the body of the table
	 * @author oderah
	 * 
	 * @return a TableBody component with TableRow components
	 * 			which contain info from state.bodyData mapped to
	 * 			TableCell components
	 */
    const Body = (props: BodyProps): JSX.Element => {
        const state = useContext(StateContext);
        const { striped, actions } = props;
        var hasActions = (actions)? true : false;

        // determine what page to display
        var page: DataRow[] | undefined = undefined;
		if (state.pagination) {
                    var pages: DataRow[][] = _.chunk(state.bodyData, state.pagination.rowsPerPage);
			page = pages[state.pagination.currentPageIndex];
        } else page = state.bodyData;
        
		return (
            <TableBody className={ (elevated) ? 'elevated-table' : '' }>
                {
                    page && page.map((row: DataRow, index: number) =>
                    (<TableRow className={ (striped && index % 2 !== 0) ?  'dark-row' : 'light-row'} 
                        hover key={ index } children={ orderByHeader(row, state.headerData, hasActions).map((data: any, index: number) =>
                            <TableCell key={ index } children={ data } />) } />))
                }
            </TableBody>
        );
    }
    
    /**
	 * changes the number of rows displayed per page
	 * @author oderah
	 * 
	 * @param $event change event containing the new value
     * @param dispatch a function that sends an action to the reducer
	 */
	const changeRowsPerPage = ($event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, dispatch: Function) => {
        dispatch({
            type: 'updatePagination',
            payload: {
                currentPageIndex: 0,
                rowsPerPage: parseInt($event.target.value, 10)
            }
        })
	}

    /**
	 * creates rows for the footer of the table
	 * @author oderah
	 * 
	 * @return a TableFooter component with a TableRow component containing the custom footer element and
	 * 			pagination if enabled
	 */
    const Footer = (props: PaginationOptions): JSX.Element => {
        const state = useContext(StateContext);
        const dispatch = useContext(DispatchContext);

        /**
         * navigation buttons for pagination
         * @author oderah
         * 
         * @return a list of buttons for page navigation
         */
        const paginationNavActions = (): JSX.Element => {
            // index of the last page
            var lastPageIndex = (state.pagination) ? Math.ceil(state.bodyData.length / state.pagination.rowsPerPage) - 1 : 0;
           
            // index of the current page
            var currentPageIndex = (state.pagination) ? state.pagination.currentPageIndex : 0;
            
            // number of rows per page
            var rowsPerPage = (state.pagination) ? state.pagination.rowsPerPage : 0;
            return (
                <div className="d-flex flex-row ml-auto">
                    <IconButton
                        onClick={ () => { dispatch({ type: 'updatePagination', payload: { currentPageIndex: 0, rowsPerPage: rowsPerPage } }); } }
                        disabled={ currentPageIndex <= 0 }
                        aria-label="first  page">
                            { <FirstPageIcon /> }
                    </IconButton>
                
                    <IconButton
                        onClick={ () => { dispatch({ type: 'updatePagination', payload: { currentPageIndex: currentPageIndex - 1, rowsPerPage: rowsPerPage } }); } }
                        disabled={ currentPageIndex <= 0 }
                        aria-label="previous page">
                            { <KeyboardArrowLeft /> }
                    </IconButton>
                
                    <IconButton
                        onClick={ () => { dispatch({ type: 'updatePagination', payload: { currentPageIndex: currentPageIndex + 1, rowsPerPage: rowsPerPage } }); } }
                        disabled={ currentPageIndex >= lastPageIndex }
                        aria-label="next page">
                            { <KeyboardArrowRight />}
                    </IconButton>
            
                    <IconButton
                        onClick={ () => { dispatch({ type: 'updatePagination', payload: { currentPageIndex: lastPageIndex, rowsPerPage: rowsPerPage } }); } }
                        disabled={ currentPageIndex >= lastPageIndex }
                        aria-label="last page">
                            { <LastPageIcon />  }
                    </IconButton>
                </div>
            );
        }

        return (
            <TableFooter>
                {
                    state.footerData && (
                        <TableRow className="footer-row">
                            <TableCell colSpan={ state.headerData.length } children={ state.footerData } />
                        </TableRow>
                    )
                }
                {
                    state.pagination && props && (
                        <TableRow>
                            <TablePagination
                                rowsPerPageOptions={ props.rowsPerPageOptions }
                                colSpan={ (props.colSpan) ? props.colSpan : state.headerData.length }
                                count={ state.bodyData.length }
                                rowsPerPage={ state.pagination.rowsPerPage }
                                page={ state.pagination.currentPageIndex }
                                onPageChange={ (_event, page) => {
                                    dispatch({
                                        type: 'updatePagination',
                                        payload: { currentPageIndex: page, rowsPerPage: state.pagination!.rowsPerPage }
                                    });
                                } }
                                onRowsPerPageChange={ $event => { changeRowsPerPage($event, dispatch) } }
                                ActionsComponent={ paginationNavActions } 
                                className="ml-auto" />
                        </TableRow>
                    )
                }
            </TableFooter>
        );
    }

    // table props
    const { header, body, striped, pagination, actions, sortable, missingValue, footer, elevated, sort } = props;

    
    // add "Actions" column to header
    var containsActions = header.find(x => 'actions' === x.id);
    if (actions && !containsActions) {
        header.push({ id: 'actions', title: 'Actions' });
    }

    // initial state of the table
    var initialState: TableState = {
        headerData: header,
        bodyData: body,
        footerData: (footer) ? footer : undefined,
        sortBy: {
            id: (sort) ? sort.id : '',
            order: (sort) ? sort.order : 'asc'
        },
        pagination: (!pagination) ? undefined : {
            currentPageIndex: (pagination.currentPage) ? pagination.currentPage : 0,
            rowsPerPage: pagination.rowsPerPage
        }
    };

    const [ state, dispatch ] = useReducer(tableReducer, initialState);

    // create contexts
    const DispatchContext = React.createContext(dispatch);
    const StateContext = React.createContext(initialState);
    
    // initial sort
    useEffect(() => {
        dispatch({
            type: 'initialSort',
            payload: {}
        });
    }, []);

    return (
        <Table>
            <StateContext.Provider value={ state }>
                <DispatchContext.Provider value={ dispatch }>
                    <Header sortable={ sortable }></Header>
                </DispatchContext.Provider>
                <Body striped={ striped } actions={ actions } missingValue={ missingValue }></Body>
                <DispatchContext.Provider value={ dispatch }>
                    {
                        (pagination) ? 
                        <Footer rowsPerPageOptions={ pagination.rowsPerPageOptions }
                        colSpan={ (pagination.colSpan)? pagination.colSpan : undefined }
                        rowsPerPage={ pagination.rowsPerPage }
                        currentPage={ (pagination.currentPage) ? pagination.currentPage: undefined }></Footer>:
                        <Footer rowsPerPageOptions={ [] } rowsPerPage={ -1 }></Footer>
                    }
                </DispatchContext.Provider>
            </StateContext.Provider>
        </Table>
    );
}

export default InterestifyTable;
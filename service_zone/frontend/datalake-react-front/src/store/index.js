import { combineReducers } from "redux"
import { containerReducer } from "./containerReducer"

const allReducers = combineReducers({
    nameContainer: containerReducer,
})

export default allReducers
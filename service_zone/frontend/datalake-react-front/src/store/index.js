import { combineReducers } from "redux"
import { containerReducer } from "./containerReducer"
import { authReducer } from "./authReducer";


const allReducers = combineReducers({
    nameContainer: containerReducer,
    auth: authReducer
})

export default allReducers
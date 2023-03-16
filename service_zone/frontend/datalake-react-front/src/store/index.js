import { combineReducers } from "redux"
import { containerReducer } from "./Container/containerReducer"
import { authReducer } from "./Auth/authReducer";
import {similarityReducer} from "./Similarity/similarityReducer";
import {traceabilityReducer} from "./Traceability/traceabilityReducer";



const allReducers = combineReducers({
    nameContainer: containerReducer,
    auth: authReducer,
    similarity: similarityReducer,
    traceability: traceabilityReducer
})

export default allReducers
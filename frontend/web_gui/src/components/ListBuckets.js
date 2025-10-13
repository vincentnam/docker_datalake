import React, { useEffect, useState } from "react";
import mc from "../utils/mc";

import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import NewBucket from "./NewBucket/NewBucket";
import { Toast } from "primereact/toast";
import useToast from "../hooks/useToast";

const ListBuckets = () => {

  const [buckets, setBuckets] = useState([]);
  const [toast, showError, showSuccess] = useToast();

  const getBuckets = async () => {
    const res = await mc.listBuckets();
    setBuckets(res);
  };


  const removeBucket =async (node) => {
    try {
      await mc.removeBucket(node.name)

      showSuccess("Successfully removed bucket")
    }catch (er){
      showError("Tested Error:",er.message)
      console.log("showError")
    }

    await getBuckets()

  }

  useEffect(() => {
    getBuckets();
  }, []);

  const bucketsTableHeader=() => {
    return (
      <div className="flex justify-between align-items-center gap-10">
        <h5 className="m-0">Buckets</h5>
        <NewBucket onRefresh={getBuckets} />
      </div>
    )
  }


  const actionTemplate = (node, column) => {
    return <div className="flex gap-2">
      <button type="button" className="bg-white hover:bg-gray-200 flex items-center p-1 rounded" onClick={()=>{
        removeBucket(node)}
      }>
        <i className=" pi pi-trash"></i>
      </button>

    </div>
  }



  return (
    <>
      <Toast ref={toast} />
      <div className="flex flex-1">
      <DataTable value={buckets}   width="100%" style={{flex:1, border:"1px solid #CECEEC" , borderRadius:"5px"}} header={bucketsTableHeader}>
        <Column field="name"  width={"80%"} header="Name" body={(rowData)=>{
          return <a className="text-pink-700 underline hover:text-blue-800" href={`/buckets/${rowData.name}`} rel="noopener">{rowData.name} </a>;

        }}/>
        <Column field="creationDate" header="Created At" style={{width:"220px"}} body={(rowData=>{
          return <span>
            {new Date(rowData.creationDate).toLocaleString()}
          </span>
        })}></Column>

        <Column body={actionTemplate} style={{ textAlign: 'center', width: '80px' }} />

      </DataTable>
      </div>

      </>

  );
};

export default ListBuckets;
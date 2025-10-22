// import React, { useEffect, useState } from "react";
// import mc from "../utils/mc";
// import {getBuckets, removeBucket, createBucket} from "../utils/s3client";
// import { DataTable } from "primereact/datatable";
// import { Column } from "primereact/column";
// import NewBucket from "./NewBucket/NewBucket";
// import { Toast } from "primereact/toast";
// import useToast from "../hooks/useToast";
//
// const ListBuckets = () => {
//   const API_BASE_URL = "http://localhost:5000/"
//   const [buckets, setBuckets] = useState([]);
//   const [toast, showError, showSuccess] = useToast();
//   const token = localStorage.getItem('jwtToken');  // Récupérez JWT stocké (ex. post-login)
//
//
//   // const getBuckets = async () => {
//   //   // const res = await mc.listBuckets();
//   //
//   //     const response = await fetch(API_BASE_URL+'buckets', {
//   //       method: 'GET',
//   //       signal: AbortSignal.timeout(5000),
//   //       headers: {
//   //         'Authorization': `Bearer ${token}`,
//   //         'Content-Type': 'application/json',
//   //       },
//   //     });
//   //     const res = await response.json();
//   //   setBuckets(res.buckets);
//   //   console.log(res.buckets)
//   // };
//   //
//   // const createBucket = async (bucketName) => {
//   //   const token = localStorage.getItem('jwtToken');
//   //   const response = await fetch('http://localhost:5000/buckets', {
//   //     method: 'POST',
//   //     signal: AbortSignal.timeout(5000),
//   //     headers: {
//   //       'Authorization': `Bearer ${token}`,
//   //       'Content-Type': 'application/json',
//   //     },
//   //     body: JSON.stringify({ name: bucketName }),
//   //   });
//   //   if (!response.ok) showError(`HTTP ${response.status}` + ":" + response.statusText);
//   //   return response.json();
//   // };
//
//
//
//   const removeBucket =async (node) => {
//     try {
//
//       // await mc.removeBucket(node.name)
//       const response = await fetch('http://localhost:5000/buckets', {
//         method: 'GET',
//         signal: AbortSignal.timeout(5000),
//         headers: {
//           'Authorization': `Bearer ${token}`,
//           'Content-Type': 'application/json',
//         },
//       });
//       showSuccess("Successfully removed bucket")
//     }catch (er){
//       showError("Tested Error:",er.message)
//       console.log("showError")
//     }
//
//     await getBuckets()
//
//   }
//
//   useEffect(() => {
//     setBuckets(getBuckets());
//     console.log(buckets)
//   }, []);
//
//   const bucketsTableHeader=() => {
//     return (
//       <div className="flex justify-between align-items-center gap-10">
//         <h5 className="m-0">Buckets</h5>
//         <NewBucket onRefresh={getBuckets} />
//       </div>
//     )
//   }
//
//
//   const actionTemplate = (node, column) => {
//     return <div className="flex gap-2">
//       <button type="button" className="bg-white hover:bg-gray-200 flex items-center p-1 rounded" onClick={()=>{
//         removeBucket(node)}
//       }>
//         <i className=" pi pi-trash"></i>
//       </button>
//
//     </div>
//   }
//
//
//
//   return (
//     <>
//       <Toast ref={toast} />
//       <div className="flex flex-1">
//       <DataTable value={buckets}   width="100%" style={{flex:1, border:"1px solid #CECEEC" , borderRadius:"5px"}} header={bucketsTableHeader}>
//         <Column field="name"  width={"80%"} header="Name" body={(rowData)=>{
//           return <a className="text-pink-700 underline hover:text-blue-800" href={`/buckets/${rowData.name}`} rel="noopener">{rowData.name} </a>;
//
//         }}/>
//         <Column field="creationDate" header="Created At" style={{width:"220px"}} body={(rowData=>{
//           return <span>
//             {new Date(rowData.creationDate).toLocaleString()}
//           </span>
//         })}></Column>
//
//         <Column body={actionTemplate} style={{ textAlign: 'center', width: '80px' }} />
//
//       </DataTable>
//       </div>
//
//       </>
//
//   );
// };
//
// export default ListBuckets;

import React, { useEffect, useState } from "react";
import { getBuckets, removeBucket } from "../utils/s3client"; // Assurez-vous que removeBucket est défini dans s3client.js
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import NewBucket from "./NewBucket/NewBucket";
import { Toast } from "primereact/toast";
import useToast from "../hooks/useToast";

const ListBuckets = () => {
  const [buckets, setBuckets] = useState([]);
  const [toast, showError, showSuccess] = useToast();

  const fetchBuckets = async () => {
    try {
      const data = await getBuckets();
      setBuckets(data);
    } catch (err) {
      showError(`Erreur: ${err.message}`);
    }
  };
  //
  // const removeBucket = async (node) => {
  //   try {
  //     await fetch(`http://localhost:5000/buckets/${node.name}`, { // Assumé DELETE /buckets/:name ; adaptez si différent
  //       method: 'DELETE',
  //       headers: {
  //         'Authorization': `Bearer ${localStorage.getItem('jwtToken')}`,
  //         'Content-Type': 'application/json',
  //       },
  //     });
  //     showSuccess("Successfully removed bucket");
  //     await fetchBuckets(); // Rafraîchit après suppression
  //   } catch (err) {
  //     showError(`Erreur: ${err.message}`);
  //   }
  // };

  useEffect(() => {
    fetchBuckets();
    console.log(buckets)
  }, []);

  const bucketsTableHeader = () => (
    <div className="flex justify-between align-items-center gap-10">
      <h5 className="m-0">Buckets</h5>
      <NewBucket onRefresh={fetchBuckets} />
    </div>
  );
  const handleRemoveBucket = async (node) => {
  try {
    await removeBucket(node.name || node.Name); // Adaptez au champ (name ou Name)
    showSuccess("Bucket supprimé avec succès");
    fetchBuckets(); // Rafraîchit la liste
  } catch (err) {
    showError(`Erreur lors de la suppression: ${err.message}`);
  }
};
  const actionTemplate = (node) => (
    <div className="flex gap-2">
      <button type="button" className="bg-white hover:bg-gray-200 flex items-center p-1 rounded" onClick={() => handleRemoveBucket(node)}>
        <i className="pi pi-trash"></i>
      </button>
    </div>
  );

  return (
    <>
      <Toast ref={toast} />
      <div className="flex flex-1">
        <DataTable value={buckets} style={{ flex: 1, border: "1px solid #CECEEC", borderRadius: "5px" }} header={bucketsTableHeader}>
          <Column field="name" header="Name" body={(rowData) => (
            <a className="text-pink-700 underline hover:text-blue-800" href={`/buckets/${rowData.Name}`} rel="noopener noreferrer">{rowData.Name}</a>
          )} />
          <Column field="creationDate" header="Created At" style={{ width: "220px" }} body={(rowData) => (
            <span>{new Date(rowData.CreationDate).toLocaleString()}</span>
          )} />
          <Column body={actionTemplate} style={{ textAlign: 'center', width: '80px' }} />
        </DataTable>
      </div>
    </>
  );
};

export default ListBuckets;
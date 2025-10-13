import { useRef } from "react";


const useToast= () => {
  const toast = useRef(null);


  const showSuccess = (summary = "", detail = "") => {
    toast.current.show({ severity: 'success', summary: summary, detail: detail, life: 3000 });
  }
  const showError = (summary = "", detail = "") => {
    toast.current.show({ severity: 'error', summary: summary, detail: detail, life: 3000 });
  }

  return [toast, showError, showSuccess]
}
export default useToast
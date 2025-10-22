import React, { useState } from "react";
import { Dialog } from "primereact/dialog";
import { useForm, Controller } from "react-hook-form";
import { InputText } from "primereact/inputtext";
import { Checkbox } from "primereact/checkbox";
import { classNames } from "primereact/utils";
// import mc from "../../utils/mc";
import {createBucket} from "../../utils/s3client";
import { Toast } from "primereact/toast";
import useToast from "../../hooks/useToast";


const NewBucket = ({ onRefresh }) => {
  const [displayBasic, setDisplayBasic] = useState(false);
  const [toast, showError, showSuccess] = useToast();

  const defaultValues = {
    bucketName: "",
    enableLocking: false,
    region: "us-east-1"
  };

  const { control, formState: { errors }, handleSubmit, reset } = useForm({ defaultValues });

  const onSubmit = async (data) => {
    const { bucketName, enableLocking, region } = data;
    try {
      await createBucket(bucketName, region, { ObjectLocking: enableLocking });
      reset();
      setDisplayBasic(false);
      showSuccess(`Created ${bucketName} successfully`);
      onRefresh?.();
    } catch (er) {
      showError(`Error creating ${bucketName} : ${er}`);
    }
  };

  const getFormErrorMessage = (name) => {
    return errors[name] && <small className="p-error">{errors[name].message}</small>;
  };

  return (
    <>
      <Toast ref={toast} />
      <Dialog header="Create New Bucket" visible={displayBasic} style={{ width: "50vw" }}
              onHide={() => setDisplayBasic(false)}>
        <form onSubmit={handleSubmit(onSubmit)} className="p-fluid">
          <div className="field mt-5">
            <span className="p-float-label">
              <Controller name="bucketName" control={control}
                          rules={{ required: "Name is required." }}
                          render={({ field, fieldState }) => (
                            <InputText id={field.name} {...field} autoFocus
                                       className={classNames({ "p-invalid": fieldState.invalid })} />
                          )} />
              <label htmlFor="bucketName"
                     className={classNames({ "p-error": errors.bucketName })}>Name*</label>
            </span>
            {getFormErrorMessage("bucketName")}
          </div>
          <div className="mt-10">
            <span className="p-float-label">
              <Controller name="region" control={control} render={({ field, fieldState }) => (
                <InputText id={field.name} {...field} autoFocus
                           className={classNames({ "p-invalid": fieldState.invalid })} />
              )} />
              <label htmlFor="region"
                     className={classNames({ "p-error": errors.region })}>Region</label>
            </span>
          </div>
          <div className="field-checkbox mt-5">
            <Controller name="enableLocking" control={control} render={({ field, fieldState }) => (
              <Checkbox inputId={field.name} onChange={(e) => field.onChange(e.checked)} checked={field.value}
                        className={classNames({ "p-invalid": fieldState.invalid })} />
            )} />
            <label htmlFor="enableLocking" className={classNames({ "p-error": errors.enableLocking })}>Enable Locking</label>
          </div>
          <div className="flex gap-5 items-center justify-end mt-5">
            <button className="h-12 bg-pink-800 border border-gray-100 w-24 text-white rounded" type="submit">Submit</button>
            <button className="h-12 bg-pink-800 border border-gray-100 w-24 text-white rounded" type="button" onClick={() => setDisplayBasic(false)}>Cancel</button>
          </div>
        </form>
      </Dialog>
      <button className="px-2 h-8 bg-pink-800 border border-gray-100 text-white rounded" type="button"
              onClick={() => setDisplayBasic(true)}>Create new Bucket</button>
    </>
  );
};
export default NewBucket;
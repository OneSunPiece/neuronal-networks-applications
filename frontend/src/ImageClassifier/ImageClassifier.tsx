import { useState } from "react";
import "./ImageClassifier.css";
import { PhotoIcon } from '@heroicons/react/24/solid'

export default function ImageClassifier() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [classification, setClassification] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>('Hello there!');
  
  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault(); // Prevent default form submission
  
    if (!selectedImage) {
      alert('Please select an image first.');
      return;
    }
  
    console.log('Uploading image...');
    const ENDPOINT = "https://aoeh6vcujuok4fhiqq3p3ujsiq0gyxld.lambda-url.us-east-1.on.aws/";
    setIsLoading(true);
  
    // Creating FormData object to send the file and metadata
    const formData = new FormData();
    formData.append('file', selectedImage);
    formData.append('fileName', selectedImage.name);
    formData.append('fileType', selectedImage.type);
  
    try {
      console.log('Sending image to the classifier...');
      const response = await fetch(ENDPOINT, {
        method: 'POST',
        body: formData, // Body now includes FormData
      });
      console.log('Response:', response);
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const responseData = await response.json();
      console.log('Image uploaded successfully:', responseData);
      setClassification(responseData.message);
      setMessage(`Image uploaded successfully: ${responseData.message}`);
    } catch (error) {
      console.log('Error uploading the image.');
      setMessage('Error uploading the image.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} method="POST" encType="multipart/form-data">
      <div className="space-y-12">
        <div className="border-b border-gray-900/10 pb-12">
          <h2 className="text-base/7 font-semibold text-gray-900">Image Classifier</h2>

          {classification ? 
            <p className="mt-1 text-sm/6 text-gray-600">Classification: {classification}</p>
            : 
            <p className="mt-1 text-sm/6 text-gray-600">Upload an image to classify</p>
          }

          <div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
            <div className="col-span-full">
              <label htmlFor="cover-photo" className="block text-sm/6 font-medium text-gray-900">
                Cover photo
              </label>
              
              <div className="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">
                <div className="text-center">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Selected" className="mx-auto size-12" />
                  ) : (
                    <PhotoIcon aria-hidden="true" className="mx-auto size-12 text-gray-300" />
                  )}
                  <div className="mt-4 flex text-sm/6 text-gray-600">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 focus-within:outline-hidden hover:text-indigo-500"
                    >
                      <span>Upload a file</span>
                      <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleImageChange} />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs/5 text-gray-600">PNG, JPG, GIF up to 10MB</p>
                </div>
              </div>
              
            </div>
          </div>
          {isLoading ? 
            <p className="mt-8 text-sm/6 text-gray-500">Loading...</p> 
            :
            <small className="block mt-8 text-sm/6 text-gray-500">
              {message}
            </small>
            }
        </div>
      </div>

      <div className="mt-6 flex items-center justify-end gap-x-6">
      <button
          type="submit"
          className="rounded-md bg-teal-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-teal-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
        >
          Send
        </button>
      </div>
    </form>
  )
}
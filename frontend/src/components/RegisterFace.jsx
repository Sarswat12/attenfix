import { useState, useEffect } from 'react';
import { Camera, Upload, X, AlertCircle } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';

 


export function RegisterFace({ user, onNavigate, onLogout }) {
  const [capturedImages, setCapturedImages] = useState([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);

  // TODO: Initialize real webcam access using getUserMedia API
  useEffect(() => {
    const setupCamera = async () => {
      try {
        // const stream = await navigator.mediaDevices.getUserMedia({
        //   video: { width: 640, height: 480 }
        // });
        // Reference video element and attach stream
      } catch (err) {
        setError('Camera access denied. Please enable camera permissions.');
      }
    };
    // setupCamera();
  }, []);

  const handleCapture = async () => {
    // Capture is not implemented for webcam in this simplified flow.
    // Use file upload below to select face images.
  };

  const handleRemoveImage = (index) => {
    setCapturedImages(capturedImages.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (capturedImages.length < 5) {
      setError('Please capture at least 5 images');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const { apiFetch } = await import('../api');

      // Upload each selected file as a separate enrollment request
      const uploaded = [];
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const formData = new FormData();
        formData.append('image', file, file.name);

        try {
          const res = await apiFetch('/api/face/enroll', {
            method: 'POST',
            body: formData
          });
          uploaded.push(res);
        } catch (err) {
          // collect error but continue
          console.error('Upload error for file', file.name, err);
        }
      }

      if (uploaded.length > 0) {
        setIsSubmitted(true);
        setSelectedFiles([]);
        setCapturedImages([]);
      } else {
        setError('Failed to upload images.');
      }
    } catch (err) {
      setError('Failed to register face. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilesSelected = (files) => {
    const arr = Array.from(files).slice(0, 7);
    setSelectedFiles(arr);
    setCapturedImages(arr.map(f => URL.createObjectURL(f)));
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar currentPage="register-face" onNavigate={onNavigate} userRole={user.role} />
      <div className="flex-1 flex flex-col">
        <Navbar user={user} onLogout={onLogout} />
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-gray-900 mb-2">Register Face</h1>
            <p className="text-gray-600">
              Capture multiple images of your face for accurate recognition
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Webcam Preview */}
            <Card className="p-6">
              <h2 className="text-gray-900 mb-4">Camera Preview</h2>
              <div className="aspect-video bg-gray-900 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
                {!isCapturing ? (
                  <div className="text-center">
                    <Camera className="w-16 h-16 text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-400">Camera feed will appear here</p>
                  </div>
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-blue-900 to-blue-700 flex items-center justify-center">
                    <div className="w-48 h-48 border-4 border-blue-400 rounded-full flex items-center justify-center">
                      <Camera className="w-24 h-24 text-blue-200" />
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <Button
                  onClick={() => setIsCapturing(!isCapturing)}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Camera className="w-5 h-5 mr-2" />
                  {isCapturing ? 'Stop Camera' : 'Start Camera'}
                </Button>

                <input
                  id="file-input"
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => handleFilesSelected(e.target.files)}
                  className="w-full"
                />
              </div>

              <Alert className="mt-4 border-blue-200 bg-blue-50">
                <AlertCircle className="h-4 w-4 text-blue-600" />
                <AlertDescription className="text-blue-800">
                  Please capture your face from different angles for accurate detection. Ensure
                  good lighting and look directly at the camera.
                </AlertDescription>
              </Alert>
            </Card>

            {/* Captured Images Gallery */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-gray-900">Captured Images</h2>
                <span className="text-gray-600">
                  {capturedImages.length} / 7 images
                </span>
              </div>

              {capturedImages.length === 0 ? (
                <div className="aspect-video border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">No images captured yet</p>
                    <p className="text-gray-400">Start capturing to see previews here</p>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    {capturedImages.map((image, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={image}
                          alt={`Captured ${index + 1}`}
                          className="w-full aspect-square object-cover rounded-lg border-2 border-gray-200"
                        />
                        <button
                          onClick={() => handleRemoveImage(index)}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={handleSubmit}
                    disabled={(selectedFiles.length < 5 && capturedImages.length < 5) || isSubmitted}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    {isSubmitted ? 'Training Model...' : 'Submit for Training'}
                  </Button>

                  {capturedImages.length < 5 && (
                    <p className="text-gray-500 text-center mt-2">
                      Capture at least 5 images to submit
                    </p>
                  )}

                  {isSubmitted && (
                    <Alert className="mt-4 border-green-200 bg-green-50">
                      <AlertCircle className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-green-800">
                        Your face data is being processed and trained. This may take a few moments.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}



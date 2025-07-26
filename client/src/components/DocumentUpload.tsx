import { useState, useCallback } from "react";
import { Upload, File, CheckCircle, X, AlertCircle, Clock, TrendingUp, BarChart3, Target, Lightbulb, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { fileWorkflowApi } from "@/services/api";
import { DataIngestResponse } from "@/types/api";

interface DocumentUploadProps {
  onUploadComplete: (files: File[], results?: DataIngestResponse[]) => void;
}

export const DocumentUpload = ({ onUploadComplete }: DocumentUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set());
  const [completedFiles, setCompletedFiles] = useState<Set<string>>(new Set());
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.name.endsWith(".xlsx") || file.name.endsWith(".xls") ||
               file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
               file.type === "application/vnd.ms-excel"
    );
    
    setFiles(prev => [...prev, ...droppedFiles]);
    
    // Start processing immediately for dropped files
    if (droppedFiles.length > 0) {
      handleImmediateUpload(droppedFiles);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selectedFiles]);
      
      // Start processing immediately for selected files
      if (selectedFiles.length > 0) {
        handleImmediateUpload(selectedFiles);
      }
    }
  };

  const handleImmediateUpload = async (filesToUpload: File[]) => {
    setIsProcessing(true);
    
    try {
      const results = [];

      // Upload files one by one to avoid overwhelming the server
      for (const file of filesToUpload) {
        const result = await uploadFile(file);
        results.push(result);
      }

      toast({
        title: "All Files Processed",
        description: `Successfully processed ${results.length} file(s)`,
      });

      onUploadComplete(filesToUpload, results);

      // Clear files after successful upload
      setTimeout(() => {
        setFiles([]);
        setUploadProgress({});
        setCompletedFiles(new Set());
        setIsProcessing(false);
      }, 2000);

    } catch (error) {
      console.error("Upload batch failed:", error);
      setIsProcessing(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (file: File) => {
    const fileId = `${file.name}-${file.size}`;

    try {
      setUploadingFiles(prev => new Set([...prev, fileId]));
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      const result = await fileWorkflowApi.uploadAndProcess(file, (progress) => {
        setUploadProgress(prev => ({ ...prev, [fileId]: progress }));
      });

      setCompletedFiles(prev => new Set([...prev, fileId]));
      setUploadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });

      toast({
        title: "File Processed Successfully",
        description: `${file.name} - Schema: ${result.schema_type}, Rows: ${result.processed_rows}`,
      });

      return result;
    } catch (error) {
      setUploadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });

      toast({
        title: "Upload Failed",
        description: `${file.name}: ${error instanceof Error ? error.message : "Upload failed"}`,
        variant: "destructive",
      });

      throw error;
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    await handleImmediateUpload(files);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-4 sm:space-y-6 px-4 sm:px-6 pt-8 sm:pt-12 lg:pt-16">
      {/* Header Section */}
      <div className="text-center space-y-2 sm:space-y-3">
        <h1 className="text-2xl sm:text-3xl font-bold text-primary">Data Insights and Analytics</h1>
        <div className="w-16 sm:w-20 h-1 bg-primary mx-auto rounded-full"></div>
        <p className="text-sm sm:text-base text-muted-foreground max-w-2xl mx-auto px-4">
          Advanced safety data analysis and business intelligence
        </p>
      </div>

      {/* Feature Cards Grid - Smaller Size */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 max-w-3xl mx-auto">
        <Card className="relative overflow-hidden border-0 shadow-md hover:shadow-lg transition-all duration-300">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary"></div>
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-start space-x-2 sm:space-x-3">
              <div className="p-1.5 bg-primary/10 rounded-lg flex-shrink-0">
                <Target className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Financial Overview</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">Get a concise overview of your financial data</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-0 shadow-md hover:shadow-lg transition-all duration-300">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"></div>
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-start space-x-2 sm:space-x-3">
              <div className="p-1.5 bg-blue-500/10 rounded-lg flex-shrink-0">
                <BarChart3 className="h-4 w-4 text-blue-500" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Performance Indicators</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">Identify important numbers and performance indicators</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-0 shadow-md hover:shadow-lg transition-all duration-300">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-yellow-500"></div>
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-start space-x-2 sm:space-x-3">
              <div className="p-1.5 bg-yellow-500/10 rounded-lg flex-shrink-0">
                <TrendingUp className="h-4 w-4 text-yellow-500" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Trend Analysis</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">Discover patterns across branches and time periods</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-0 shadow-md hover:shadow-lg transition-all duration-300">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-red-500"></div>
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-start space-x-2 sm:space-x-3">
              <div className="p-1.5 bg-red-500/10 rounded-lg flex-shrink-0">
                <Lightbulb className="h-4 w-4 text-red-500" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xs sm:text-sm font-semibold text-foreground mb-1">Data Highlights</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">Identify key data points and important findings</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* File Upload Section */}
      <div className="max-w-2xl mx-auto">
        {isProcessing ? (
          /* Upload Animation Card */
          <Card className="shadow-lg border-0 bg-white">
            <CardContent className="p-6 sm:p-8 text-center">
              <div className="space-y-4">
                {/* Spinning Loader */}
                <div className="flex justify-center">
                  <Loader2 className="h-10 w-10 sm:h-12 sm:w-12 text-primary animate-spin" />
                </div>
                
                {/* Upload Status */}
                <div className="space-y-2">
                  <h3 className="text-base sm:text-lg font-semibold text-primary">Uploading File</h3>
                  <p className="text-sm text-muted-foreground">Your file is being uploaded to the server...</p>
                  <p className="text-xs text-muted-foreground">This should only take a few seconds.</p>
                </div>

                {/* File Info */}
                {files.length > 0 && (
                  <div className="mt-4 sm:mt-6">
                    <div className="bg-gray-100 rounded-lg p-3 text-left">
                      <p className="text-sm text-gray-700 truncate">
                        {files[0].name}
                      </p>
                    </div>
                  </div>
                )}

                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div className="bg-primary h-1 rounded-full transition-all duration-300" 
                         style={{ width: `${uploadingFiles.size > 0 ? 50 : 100}%` }}></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          /* Normal Upload Area */
          <div
            className={`border-2 border-dashed rounded-xl p-6 sm:p-8 text-center transition-all duration-200 cursor-pointer ${
              dragOver
                ? "border-primary bg-primary/5"
                : "border-primary/30 hover:border-primary/60 bg-primary/5"
            }`}
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            <Upload className="h-10 w-10 sm:h-12 sm:w-12 mx-auto text-primary mb-3 sm:mb-4" />
            <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2">
              Drag and drop an Excel file here, or click to select
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Supported formats: .xlsx, .xls
            </p>
            <input
              type="file"
              multiple
              accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
          </div>
        )}

        {/* File List - Only show when not processing */}
        {!isProcessing && files.length > 0 && (
          <div className="mt-4 sm:mt-6 space-y-3">
            <h3 className="font-medium text-primary text-sm sm:text-base">Selected Files:</h3>
            {files.map((file, index) => {
              const fileId = `${file.name}-${file.size}`;
              const isUploading = uploadingFiles.has(fileId);
              const isCompleted = completedFiles.has(fileId);
              const progress = uploadProgress[fileId] || 0;

              return (
                <div
                  key={index}
                  className="p-3 border border-primary/20 rounded-lg bg-gradient-to-r from-primary/5 to-primary/10 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                      {isCompleted ? (
                        <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                      ) : isUploading ? (
                        <Clock className="h-4 w-4 text-primary animate-spin flex-shrink-0" />
                      ) : (
                        <File className="h-4 w-4 text-primary flex-shrink-0" />
                      )}
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium truncate">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                          {isCompleted && " • Processed"}
                          {isUploading && " • Processing..."}
                        </p>
                      </div>
                    </div>
                    {!isUploading && !isCompleted && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(index);
                        }}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>

                  {isUploading && (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">
                          {progress < 25 ? "Getting upload URL..." :
                           progress < 60 ? "Uploading to S3..." :
                           progress < 100 ? "Processing data..." : "Complete"}
                        </span>
                        <span className="font-medium text-primary">{progress}%</span>
                      </div>
                      <Progress value={progress} className="h-1 bg-primary/20" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Upload Progress - Only show when not processing */}
        {!isProcessing && uploadingFiles.size > 0 && (
          <div className="mt-4 sm:mt-6 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-primary font-medium">Processing {uploadingFiles.size} file(s)...</span>
              <span className="text-primary font-medium">{completedFiles.size}/{files.length} completed</span>
            </div>
            <Progress
              value={files.length > 0 ? (completedFiles.size / files.length) * 100 : 0}
              className="h-2 bg-primary/20"
            />
          </div>
        )}

        {/* Action Buttons - Only show when not processing */}
        {!isProcessing && files.length > 0 && (
          <div className="mt-4 sm:mt-6 flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              onClick={handleUpload}
              disabled={uploadingFiles.size > 0}
              className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground shadow-lg hover:shadow-primary/25 transition-all duration-200 px-6 py-2 h-10 sm:h-11 text-sm sm:text-base font-medium"
            >
              {uploadingFiles.size > 0 ? (
                <>Processing {uploadingFiles.size} files...</>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload & Process ({files.length} files)
                </>
              )}
            </Button>

            {uploadingFiles.size === 0 && (
              <Button
                variant="outline"
                onClick={() => {
                  setFiles([]);
                  setUploadProgress({});
                  setCompletedFiles(new Set());
                }}
                className="border-primary/30 text-primary hover:bg-primary/10 px-6 py-2 h-10 sm:h-11 text-sm sm:text-base font-medium"
              >
                Clear All
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
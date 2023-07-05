import numpy as np
import depthai as dai
import time


class VideoCapture:
    def __init__(self):
        self.frame_width = 1280
        self.frame_height = 720
        self.pipeline = dai.Pipeline()
        self.device = dai.Device()
        caliData = self.device.readCalibration()
        self.camera_matrix = np.array(
            caliData.getCameraIntrinsics(
                dai.CameraBoardSocket.RGB, self.frame_width, self.frame_height
            ),
            dtype=float,
        )
        self.camera_distortion = np.array(
            caliData.getDistortionCoefficients(dai.CameraBoardSocket.RGB)
        )
        self.focal_length = (
            self.camera_matrix[0, 0] + self.camera_matrix[1, 1]) / 2
        self.use_depth = False
        self.build_pipeline_without_depth()
        self.device.startPipeline(self.pipeline)
        self.qSpatial = None
        self.spatialCalcConfigInQueue = None
        self.qRgb = self.device.getOutputQueue("rgb", 1, blocking=False)
        self.qRgbEnc = self.device.getOutputQueue(
            "h264", maxSize=60, blocking=True)
        self.video_file = None
        self.current_writting_video_name = ""

    def deactivate(self):
        self.device.close()

    def switch_to_depth_pipeline(self):
        self.device.close()
        device = dai.Device()
        self.pipeline = dai.Pipeline()
        self.use_depth = True
        self.build_pipeline_with_depth()
        device.startPipeline(self.pipeline)
        self.device = device
        self.qRgb = self.device.getOutputQueue("rgb", 1, blocking=False)
        self.qRgbEnc = None
        self.qSpatial = self.device.getOutputQueue(
            "spatialData", 1, blocking=False)
        self.spatialCalcConfigInQueue = self.device.getInputQueue(
            "spatialCalcConfig")
        time.sleep(1)

    def switch_to_rgb_pipeline(self):
        self.device.close()
        device = dai.Device()
        self.pipeline = dai.Pipeline()
        self.use_depth = False
        self.build_pipeline_without_depth()
        device.startPipeline(self.pipeline)
        self.device = device
        self.qSpatial = None
        self.spatialCalcConfigInQueue = None
        self.qRgb = self.device.getOutputQueue("rgb", 1, blocking=False)
        self.qRgbEnc = self.device.getOutputQueue(
            "h264", maxSize=60, blocking=True)
        self.qSpatial = None
        self.spatialCalcConfigInQueue = None
        time.sleep(1)

    def build_pipeline_without_depth(self):
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        camRgb.setResolution(
            dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        videoEncoder = self.pipeline.create(dai.node.VideoEncoder)
        videoEncoder.setDefaultProfilePreset(
            60, dai.VideoEncoderProperties.Profile.H264_MAIN
        )
        camRgb.setFps(60)
        camRgb.setPreviewSize(1280, 720)
        camRgb.setInterleaved(False)

        xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        videoOut = self.pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        videoOut.setStreamName("h264")
        xoutRgb.input.setQueueSize(1)
        xoutRgb.input.setBlocking(False)
        camRgb.preview.link(xoutRgb.input)
        camRgb.video.link(videoEncoder.input)
        videoEncoder.bitstream.link(videoOut.input)

    def build_pipeline_with_depth(self):
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        camRgb.setResolution(
            dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        camRgb.setIspScale(2, 3)
        camRgb.setPreviewSize(1280, 720)
        camRgb.setInterleaved(False)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        xoutRgb.input.setQueueSize(1)
        xoutRgb.input.setBlocking(False)
        camRgb.preview.link(xoutRgb.input)

        left = self.pipeline.create(dai.node.MonoCamera)
        right = self.pipeline.create(dai.node.MonoCamera)
        stereo = self.pipeline.create(dai.node.StereoDepth)
        spatialLocationCalculator = self.pipeline.create(
            dai.node.SpatialLocationCalculator
        )
        monoResolution = dai.MonoCameraProperties.SensorResolution.THE_400_P
        left.setResolution(monoResolution)
        left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        right.setResolution(monoResolution)
        right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        stereo.setDefaultProfilePreset(
            dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        # LR-check is required for depth alignment
        stereo.setLeftRightCheck(True)
        stereo.setSubpixel(False)
        stereo.setExtendedDisparity(True)
        stereo.setDepthAlign(dai.CameraBoardSocket.RGB)

        left.out.link(stereo.left)
        right.out.link(stereo.right)

        xoutSpatialData = self.pipeline.create(dai.node.XLinkOut)
        xoutSpatialData.input.setQueueSize(1)
        xoutSpatialData.input.setBlocking(False)
        xinSpatialCalcConfig = self.pipeline.create(dai.node.XLinkIn)
        xoutSpatialData.setStreamName("spatialData")
        xinSpatialCalcConfig.setStreamName("spatialCalcConfig")
        # Config
        topLeft = dai.Point2f(0.49, 0.49)
        bottomRight = dai.Point2f(0.51, 0.51)

        config = dai.SpatialLocationCalculatorConfigData()
        config.depthThresholds.lowerThreshold = 100
        config.depthThresholds.upperThreshold = 10000
        config.roi = dai.Rect(topLeft, bottomRight)
        spatialLocationCalculator.inputConfig.setWaitForMessage(False)
        spatialLocationCalculator.setWaitForConfigInput(True)
        spatialLocationCalculator.initialConfig.addROI(config)
        spatialLocationCalculator.inputDepth.setBlocking(False)
        spatialLocationCalculator.inputDepth.setQueueSize(1)
        stereo.depth.link(spatialLocationCalculator.inputDepth)
        spatialLocationCalculator.out.link(xoutSpatialData.input)
        xinSpatialCalcConfig.out.link(spatialLocationCalculator.inputConfig)

    def reset_video(self):
        if self.video_file is not None:
            self.video_file.close()
            self.video_file = None
            self.current_writting_video_name = ""
        return True

    def open_new_video(self, video_file):
        if self.video_file is None:
            self.current_writting_video_name = video_file
        else:
            self.video_file.close()
            self.video_file = None
            self.current_writting_video_name = video_file
        return True

    def get_frame(self, video_file=None, save_path=None):
        frame = self.qRgb.get().getCvFrame()
        if not self.use_depth:
            while self.qRgbEnc.has():
                if video_file:
                    base_path = "./saved_videos/"
                    if save_path is not None:
                        base_path = save_path
                    if self.video_file is None:
                        self.video_file = open(
                            base_path + video_file + ".h264", "w+b")
                        self.current_writting_video_name = video_file
                    else:
                        if video_file != self.current_writting_video_name:
                            self.video_file.close()
                            self.video_file = open(
                                base_path + video_file + ".h264", "w+b"
                            )
                            self.current_writting_video_name = video_file
                    if self.video_file is None:
                        self.video_file = open(
                            base_path + video_file + ".h264", "w+b")
                    self.qRgbEnc.get().getData().tofile(self.video_file)
                else:
                    self.qRgbEnc.get()
        return frame

    def get_depth(self, rois):
        if self.use_depth:
            cfg = dai.SpatialLocationCalculatorConfig()
            for roi in rois:
                config = dai.SpatialLocationCalculatorConfigData()
                config.depthThresholds.lowerThreshold = 100
                config.depthThresholds.upperThreshold = 10000
                topLeft = dai.Point2f(roi[0], roi[1])
                bottomRight = dai.Point2f(roi[2], roi[3])
                config.roi = dai.Rect(topLeft, bottomRight)
                config.calculationAlgorithm = (
                    dai.SpatialLocationCalculatorAlgorithm.AVERAGE
                )
                cfg.addROI(config)
            self.spatialCalcConfigInQueue.send(cfg)
            spatialData = self.qSpatial.get().getSpatialLocations()
            return spatialData
        else:
            return []

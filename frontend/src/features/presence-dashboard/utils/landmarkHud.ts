export type PoseLandmark = {
  x: number;
  y: number;
  visibility?: number;
};

export type HolisticResults = {
  faceLandmarks?: PoseLandmark[];
  poseLandmarks?: PoseLandmark[];
  leftHandLandmarks?: PoseLandmark[];
  rightHandLandmarks?: PoseLandmark[];
};

type Connection = readonly [number, number];

const LANDMARK_COLOR = "rgb(0, 209, 255)";
const LANDMARK_FILL = LANDMARK_COLOR;
const LANDMARK_SHADOW = "rgba(0, 209, 255, 0.35)";
const LANDMARK_ALPHA = 0.58;
const LANDMARK_POINT_RADIUS = 1.45;

const FACE_POINTS = [
  10, 67, 297, 54, 284, 162, 389, 93, 323, 172, 397,
  127, 356,
  149, 378, 152,
  168, 6, 197, 5, 98, 327,
  70, 105, 107, 336, 334, 300,
  33, 159, 133, 145, 468,
  362, 386, 263, 374, 473,
  61, 291,
  0, 37, 267,
  13, 14, 17, 84, 314,
] as const;

const FACE_CONNECTIONS: readonly Connection[] = [
  [10, 67], [67, 54], [54, 162], [162, 127], [127, 93], [93, 172], [172, 149], [149, 152],
  [10, 297], [297, 284], [284, 389], [389, 356], [356, 323], [323, 397], [397, 378], [378, 152],
  [10, 168], [168, 6], [6, 197], [197, 5],
  [5, 98], [5, 327],
  [98, 327],
  [93, 98], [323, 327],
  [70, 105], [105, 107],
  [336, 334], [334, 300],
  [70, 162], [336, 168],
  [107, 168], [300, 389],
  [33, 159], [159, 133], [133, 145], [145, 33],
  [159, 468], [145, 468], [33, 468], [133, 468],
  [362, 386], [386, 263], [263, 374], [374, 362],
  [386, 473], [374, 473], [362, 473], [263, 473],
  [6, 362], [6, 133],
  [127, 33], [356, 263],
  [133, 98], [362, 327],
  [61, 37], [37, 0], [0, 13],
  [291, 267], [267, 0], [291, 13], [61, 13],
  [61, 84], [84, 17], [314, 17],
  [291, 314], [84, 14], [314, 14],
  [17, 152],
  [37, 13], [267, 13],
  [13, 14],
  [13, 291],
  [61, 14], [14, 291],
  [172, 61], [397, 291],
  [98, 61], [327, 291],
] as const;

const BODY_POINTS = [
  0,
  11, 12,
  13, 14,
  15, 16,
  23, 24,
  25, 26,
  27, 28,
  29, 30,
  31, 32,
] as const;

const BODY_CONNECTIONS: readonly Connection[] = [
  [11, 12],
  [11, 23],
  [12, 24],
  [23, 24],
  [23, 11],
  [24, 12],
  [11, 13], [13, 15],
  [12, 14], [14, 16],
  [23, 25], [25, 27], [27, 29], [29, 31],
  [24, 26], [26, 28], [28, 30], [30, 32],
] as const;

const HAND_POINTS = Array.from({ length: 21 }, (_, index) => index);

const HAND_CONNECTIONS: readonly Connection[] = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [0, 9], [9, 10], [10, 11], [11, 12],
  [0, 13], [13, 14], [14, 15], [15, 16],
  [0, 17], [17, 18], [18, 19], [19, 20],
] as const;

const pointRadius = (width: number, height: number, scale: number, min: number) =>
  Math.max(min, Math.min(width, height) * scale);

const drawConnections = (
  context: CanvasRenderingContext2D,
  landmarks: PoseLandmark[],
  connections: readonly Connection[],
  width: number,
  height: number,
) => {
  connections.forEach(([fromIndex, toIndex]) => {
    const from = landmarks[fromIndex];
    const to = landmarks[toIndex];

    if (!from || !to) {
      return;
    }

    context.beginPath();
    context.moveTo(from.x * width, from.y * height);
    context.lineTo(to.x * width, to.y * height);
    context.stroke();
  });
};

const drawPoints = (
  context: CanvasRenderingContext2D,
  landmarks: PoseLandmark[],
  points: readonly number[],
  width: number,
  height: number,
  radius: number,
) => {
  points.forEach((index) => {
    const landmark = landmarks[index];

    if (!landmark) {
      return;
    }

    context.beginPath();
    context.arc(landmark.x * width, landmark.y * height, radius, 0, Math.PI * 2);
    context.fill();
    context.stroke();
  });
};

const drawBodyHud = (
  context: CanvasRenderingContext2D,
  landmarks: PoseLandmark[],
  width: number,
  height: number,
) => {
  if (!landmarks.length) {
    return;
  }

  context.save();
  context.lineCap = "round";
  context.lineJoin = "round";
  context.strokeStyle = LANDMARK_COLOR;
  context.globalAlpha = LANDMARK_ALPHA;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);
  context.shadowColor = LANDMARK_SHADOW;
  context.shadowBlur = 4;
  drawConnections(context, landmarks, BODY_CONNECTIONS, width, height);

  context.fillStyle = LANDMARK_FILL;
  context.strokeStyle = LANDMARK_COLOR;
  context.globalAlpha = LANDMARK_ALPHA;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);
  drawPoints(context, landmarks, BODY_POINTS, width, height, LANDMARK_POINT_RADIUS);
  context.restore();
};

const drawHandHud = (
  context: CanvasRenderingContext2D,
  landmarks: PoseLandmark[],
  width: number,
  height: number,
) => {
  if (!landmarks.length) {
    return;
  }

  context.save();
  context.lineCap = "round";
  context.lineJoin = "round";
  context.strokeStyle = LANDMARK_COLOR;
  context.globalAlpha = LANDMARK_ALPHA;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);
  context.shadowColor = LANDMARK_SHADOW;
  context.shadowBlur = 4;
  drawConnections(context, landmarks, HAND_CONNECTIONS, width, height);

  context.fillStyle = LANDMARK_FILL;
  context.strokeStyle = LANDMARK_COLOR;
  context.globalAlpha = LANDMARK_ALPHA;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);
  drawPoints(context, landmarks, HAND_POINTS, width, height, LANDMARK_POINT_RADIUS);
  context.restore();
};

const drawFaceHud = (
  context: CanvasRenderingContext2D,
  landmarks: PoseLandmark[],
  width: number,
  height: number,
) => {
  if (!landmarks.length) {
    return;
  }

  context.save();
  context.lineCap = "round";
  context.lineJoin = "round";
  context.strokeStyle = LANDMARK_COLOR;
  context.shadowColor = LANDMARK_SHADOW;
  context.shadowBlur = 4;
  context.globalAlpha = LANDMARK_ALPHA;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);

  FACE_CONNECTIONS.forEach(([fromIndex, toIndex]) => {
    const from = landmarks[fromIndex];
    const to = landmarks[toIndex];

    if (!from || !to) {
      return;
    }

    context.beginPath();
    context.moveTo(from.x * width, from.y * height);
    context.lineTo(to.x * width, to.y * height);
    context.stroke();
  });

  context.fillStyle = LANDMARK_FILL;
  context.strokeStyle = LANDMARK_COLOR;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);
  context.globalAlpha = LANDMARK_ALPHA;

  FACE_POINTS.forEach((index) => {
    const landmark = landmarks[index];

    if (!landmark) {
      return;
    }

    context.beginPath();
    context.arc(landmark.x * width, landmark.y * height, LANDMARK_POINT_RADIUS, 0, Math.PI * 2);
    context.fill();
    context.stroke();
  });

  context.restore();
};

const drawChinToShouldersHud = (
  context: CanvasRenderingContext2D,
  faceLandmarks: PoseLandmark[],
  poseLandmarks: PoseLandmark[],
  width: number,
  height: number,
) => {
  const chin = faceLandmarks[152];
  const leftShoulder = poseLandmarks[11];
  const rightShoulder = poseLandmarks[12];

  if (!chin || !leftShoulder || !rightShoulder) {
    return;
  }

  const shoulderCenter = {
    x: (leftShoulder.x + rightShoulder.x) / 2,
    y: (leftShoulder.y + rightShoulder.y) / 2,
  };

  context.save();
  context.lineCap = "round";
  context.lineJoin = "round";
  context.strokeStyle = LANDMARK_COLOR;
  context.globalAlpha = LANDMARK_ALPHA;
  context.lineWidth = pointRadius(width, height, 0.0012, 0.9);
  context.shadowColor = LANDMARK_SHADOW;
  context.shadowBlur = 4;
  context.beginPath();
  context.moveTo(chin.x * width, chin.y * height);
  context.lineTo(shoulderCenter.x * width, shoulderCenter.y * height);
  context.stroke();
  context.restore();
};

export const drawHolisticHud = (canvas: HTMLCanvasElement, results: HolisticResults = {}) => {
  const context = canvas.getContext("2d");

  if (!context) {
    return;
  }

  context.clearRect(0, 0, canvas.width, canvas.height);
  drawBodyHud(context, results.poseLandmarks ?? [], canvas.width, canvas.height);
  drawHandHud(context, results.leftHandLandmarks ?? [], canvas.width, canvas.height);
  drawHandHud(context, results.rightHandLandmarks ?? [], canvas.width, canvas.height);
  drawFaceHud(context, results.faceLandmarks ?? [], canvas.width, canvas.height);
  drawChinToShouldersHud(
    context,
    results.faceLandmarks ?? [],
    results.poseLandmarks ?? [],
    canvas.width,
    canvas.height,
  );
};

import {
  FileVideoCamera,
  Image as ImageIcon,
  Captions,
  FileQuestionMark,
  MessagesSquare,
} from "lucide-react";
import { type AssetFormData, type ModalityOption } from "@/types/asset.types";

export const ASSET_MODALITY_OPTIONS: ModalityOption[] = [
  { label: "Video", value: "video", icon: FileVideoCamera },
  { label: "Image", value: "image", icon: ImageIcon },
  { label: "Transcript", value: "transcript", icon: Captions },
  { label: "Quiz", value: "quiz", icon: FileQuestionMark },
  { label: "Discussion Thread", value: "discussion", icon: MessagesSquare },
];

export const DEFAULT_ASSET_FORM_VALUES: AssetFormData = {
  title: "",
  modality: "transcript",
  owner: "",
  storageUrl: "",
  conceptTags: "",
};

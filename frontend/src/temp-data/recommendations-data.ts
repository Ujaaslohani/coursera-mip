import { Recommendation } from "@/types";

export const mockRecommendations: Recommendation[] = [
  {
    id: "rec-1",
    title:
      "Relationship between regularization parameters like lambda and the learning rate is causing further misunderstanding",
    queryBy: "query@by.com",
    category: "Model Optimization",
    description:
      "Students repeatedly confuse the convergence effects of high learning rates with underfitting from heavy L2 penalty.",
    timestamp: "10 mins ago",
    status: "curated",
    suggestedAction: "Generate Visual Explainer",
    citations: [
      {
        id: "c0b40e50...",
        type: "Transcript",
        quote:
          "Today we're covering backpropagation, the algorithm that lets neural networks learn from error.",
        explanation:
          "This evidence mentions that backpropagation allows neural networks to learn from error, indicating a foundational concept that learners need to grasp.",
      },
      {
        id: "ef66b84b...",
        type: "Image",
        quote:
          "Slide: L2 Regularization Loss = MSE + lambda * sum(w42) Confusion point: lambda strength vs learning rate",
        explanation:
          "This evidence points out the confusion related to lambda strength versus the learning rate, which is critical for understanding regularization in the context of backpropagation.",
      },
    ],
  },
  {
    id: "rec-2",
    title:
      "Backpropagation gradient vanishing in deep architectures needs intuitive visual walkthrough",
    queryBy: "analytics@coursera.org",
    category: "Neural Networks",
    description:
      "Quiz 3 drop-off spiked by 34% at question 7 regarding chain rule propagation across sigmoid activations.",
    timestamp: "35 mins ago",
    status: "curated",
    suggestedAction: "Create Video Clip",
    citations: [
      {
        id: "a81d4310...",
        type: "Transcript",
        quote:
          "When we multiply many small derivatives across layers, the gradient progressively approaches zero.",
        explanation:
          "Highlights the core mathematical breakdown where sigmoid derivatives saturate at both extremes, causing zero weight updates.",
      },
      {
        id: "b20e91fa...",
        type: "Image",
        quote:
          "Diagram: 12-layer deep sigmoid network activation gradients vs layer depth.",
        explanation:
          "Visual proof exhibiting rapid diminishing magnitude of gradient signals from output back to input layers.",
      },
    ],
  },
  {
    id: "rec-3",
    title:
      "Confusion between Cross-Entropy Loss and MSE in multiclass classification context",
    queryBy: "curriculum-bot@coursera.org",
    category: "Loss Functions",
    description:
      "High frequency of related questions on the discussion forum for Week 2 assignment submission.",
    timestamp: "1 hour ago",
    status: "pending",
    suggestedAction: "Summarize & Post FAQ",
    citations: [
      {
        id: "f44109ea...",
        type: "Transcript",
        quote:
          "Using MSE with softmax probabilities leads to non-convex optimization surfaces and sluggish convergence.",
        explanation:
          "Identifies the primary misconception learners face when selecting objective loss functions for categorical classification.",
      },
    ],
  },
  {
    id: "rec-4",
    title:
      "PCA dimensionality reduction: Variance explained ratio interpretation difficulties",
    queryBy: "telemetry@coursera.org",
    category: "Unsupervised Learning",
    description:
      "High pause and rewind rate detected around timestamp 14:20 on screencast regarding scree plots.",
    timestamp: "3 hours ago",
    status: "curated",
    suggestedAction: "Add Micro-Quiz",
    citations: [
      {
        id: "d991b101...",
        type: "Image",
        quote:
          "Figure 4.2: Cumulative explained variance ratio curve showing elbow point at k=4 components.",
        explanation:
          "Pinpoints the exact visual diagram where learners struggle to determine the cutoff threshold for principal components.",
      },
    ],
  },
  {
    id: "rec-5",
    title:
      "Overfitting vs Underfitting diagnostic curves and validation error thresholds",
    queryBy: "instructor-ops@coursera.org",
    category: "Model Evaluation",
    description:
      "Learners struggle to identify high variance vs high bias from learning curve plots.",
    timestamp: "5 hours ago",
    status: "applied",
    suggestedAction: "Review Curriculum",
    citations: [
      {
        id: "77a834cf...",
        type: "Transcript",
        quote:
          "A large gap between training accuracy and validation accuracy indicates overfitting, not underfitting.",
        explanation:
          "Provides the explicit diagnostic heuristic learners consistently invert during evaluation exercises.",
      },
    ],
  },
  {
    id: "rec-6",
    title:
      "Transformer self-attention mechanism: Query, Key, Value tensor matrix multiplication",
    queryBy: "nlp-telemetry@coursera.org",
    category: "Attention & NLP",
    description:
      "Students request step-by-step numerical breakdown for multi-head attention weights calculation.",
    timestamp: "1 day ago",
    status: "curated",
    suggestedAction: "Interactive Widget",
    citations: [
      {
        id: "55bc8120...",
        type: "Image",
        quote:
          "Matrix formula: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V",
        explanation:
          "Details the exact matrix dimensions and scaling factor causing dimensionality mismatches in homework implementations.",
      },
      {
        id: "8911ef03...",
        type: "Transcript",
        quote:
          "Each head projects Q, K, and V with separate learned linear projections before concatenation.",
        explanation:
          "Clarifies the projection step across multiple subspace representations.",
      },
    ],
  },
];

"""Generate synthetic ML lecture PDFs aligned with data/evaluation/retrieval_eval_set.csv.

Each PDF is multi-page; the page number where the relevant concept lives matches the
`relevant_page` column in the eval CSV. The text is general ML knowledge, written so
the system has something concrete to retrieve.

Run once before invoking `scripts/run_evaluation.py all`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz  # PyMuPDF

OUT_DIR = Path("data/raw/uploaded_pdfs")


def _page(text: str) -> str:
    return text.strip()


LECTURES: dict[str, list[str]] = {
    "Lecture_02_Model_Evaluation.pdf": [
        "Lecture 2 — Model Evaluation Overview\n\nThis lecture introduces the concepts used to measure how well a machine learning model performs.",
        "Why evaluation matters\n\nA model that fits training data perfectly may still fail on new examples. Evaluation gives us a principled way to estimate that real-world performance.",
        "Common evaluation metrics include accuracy, precision, recall, F1 score, and AUC. Each metric captures a different aspect of model behavior.",
        "Train-test split\n\nThe simplest way to evaluate a model is to hold out a portion of the data and train on the remaining portion. A typical split is 80 percent for training and 20 percent for testing. The test set must remain unseen during training to give an unbiased estimate of generalization performance.",
        "More on train-test split: the split must be random so the test set is representative of the underlying data distribution. Stratified splits preserve the class balance when the target labels are imbalanced.",
        "K-fold cross validation generalizes the train-test split. The data is divided into k folds and the model is trained and evaluated k times so every example is used for both training and testing.",
        "Bias-variance tradeoff: a model that is too simple underfits and has high bias, while a model that is too complex overfits and has high variance.",
    ],
    "Lecture_03_Gradient_Descent.pdf": [
        "Lecture 3 — Gradient Descent\n\nGradient descent is the foundational optimization algorithm used to train most machine learning models.",
        "Loss functions\n\nA loss function quantifies how wrong the model is for a given input-output pair. Training reduces the loss by adjusting model parameters.",
        "Gradients\n\nThe gradient of the loss with respect to the parameters indicates the direction in which the loss increases fastest. Moving in the opposite direction therefore decreases the loss.",
        "Learning rate\n\nThe learning rate controls the step size taken at each iteration. Too large a learning rate causes divergence; too small a rate causes very slow convergence.",
        "Gradient descent is an optimization algorithm that minimizes a loss function by iteratively updating model parameters in the direction opposite to the gradient. Starting from initial parameters, gradient descent repeatedly computes the gradient and takes a step of size proportional to the learning rate until convergence.",
        "Variants of gradient descent include batch gradient descent, stochastic gradient descent (SGD), and mini-batch gradient descent. SGD updates parameters using one example at a time, which introduces noise that can help escape shallow local minima.",
        "Momentum and adaptive optimizers such as Adam and RMSProp accelerate gradient descent by accumulating information about past gradients.",
        "Practical tips: shuffle the data each epoch, normalize features, monitor the training loss curve, and use a learning-rate schedule when convergence stalls.",
        "Worked example of gradient descent\n\nRecall the definition: gradient descent minimizes a loss function by iteratively updating parameters in the direction opposite to the gradient. As a concrete example, consider minimizing the loss L(w) = w^2 with learning rate 0.1, starting from w = 4. The gradient is dL/dw = 2w. Iteration 1: gradient = 8, so w becomes 4 - 0.1 * 8 = 3.2. Iteration 2: gradient = 6.4, so w becomes 3.2 - 0.64 = 2.56. Iteration 3: gradient = 5.12, so w becomes 2.56 - 0.512 = 2.048. Each iteration moves w closer to the minimum at w = 0, and the steps shrink as the gradient shrinks. Another practical example of gradient descent is fitting linear regression: each step updates the slope and intercept to reduce the mean squared error until the line best fits the data.",
    ],
    "Lecture_04_Logistic_Regression.pdf": [
        "Lecture 4 — Logistic Regression\n\nLogistic regression is a classification algorithm despite the word regression in its name.",
        "The sigmoid function maps any real value to a number between 0 and 1, which can be interpreted as a probability. It is defined as sigmoid(z) = 1 / (1 + exp(-z)). Sigmoid is monotonic, smooth, and saturates at the extremes, making it well suited for binary classification.",
        "Logistic regression models the probability that an input belongs to the positive class by passing a linear combination of features through the sigmoid function.",
        "Decision boundary\n\nWith a threshold of 0.5, logistic regression draws a linear decision boundary in the feature space. Higher thresholds favor precision over recall.",
        "Training logistic regression uses the binary cross-entropy loss, which has a convex shape that gradient descent can optimize globally.",
        "Multinomial logistic regression, also called softmax regression, generalizes the binary version to multiple classes using the softmax function.",
        "Regularization (L1 or L2) is commonly applied to logistic regression to prevent overfitting when there are many correlated features.",
    ],
    "Lecture_05_Neural_Networks.pdf": [
        "Lecture 5 — Neural Networks\n\nNeural networks are layered models that learn complex mappings from inputs to outputs.",
        "Architecture\n\nA feed-forward network is made of an input layer, one or more hidden layers, and an output layer. Each layer applies a linear transformation followed by a non-linearity.",
        "Weights and biases\n\nEach neuron has weights that scale its inputs and a bias that shifts the result. These are the trainable parameters of the network.",
        "Forward propagation passes inputs through the network to produce predictions.",
        "Backpropagation uses the chain rule of calculus to compute gradients of the loss with respect to every parameter, layer by layer.",
        "Activation functions introduce non-linearity, which is what lets a deep network represent functions a linear model cannot. Without them a deep network would collapse into a single linear transformation.",
        "Vanishing and exploding gradients are problems that arise in deep networks. Careful initialization and activation choices alleviate them.",
        "Dropout, batch normalization, and weight decay are common regularization techniques used while training neural networks.",
        "An activation function is a non-linear function applied to each neuron's output. Common choices are the rectified linear unit (ReLU), the sigmoid, and the hyperbolic tangent. ReLU is by far the most popular for hidden layers in modern deep networks because it is cheap to compute and does not saturate for positive inputs.",
        "Modern architectures include convolutional neural networks for images, recurrent networks for sequences, and transformers for language.",
    ],
    "Lecture_06_Model_Evaluation.pdf": [
        "Lecture 6 — Generalization and Overfitting\n\nThis lecture digs deeper into what it means for a model to generalize and the failure modes that prevent generalization.",
        "Training versus generalization error\n\nThe training error measures performance on data the model has seen. The generalization error measures performance on data it has not seen. The gap between the two indicates how well the model generalizes.",
        "Capacity\n\nModel capacity is the range of functions a model can represent. Higher-capacity models can fit more complex patterns but are also more prone to overfitting.",
        "Underfitting happens when capacity is too low to capture the underlying patterns in the data; both training and test errors are high.",
        "Causes of overfitting include too few training examples relative to model capacity, noisy labels, and excessive training time.",
        "Detecting overfitting is straightforward: keep a held-out validation set and watch the training and validation loss diverge as training progresses.",
        "Overfitting occurs when a model learns the training data too closely, including its noise and random fluctuations. As a consequence the model performs well on training data but poorly on new, unseen data. Overfit models have memorized rather than generalized.",
        "Regularization techniques that combat overfitting include L1 and L2 weight penalties, dropout, early stopping, and data augmentation.",
        "Cross-validation gives a more reliable estimate of generalization error than a single train-test split because every example is eventually used for validation.",
    ],
}


def write_pdf(path: Path, pages: list[str]) -> None:
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_textbox(
            fitz.Rect(72, 72, 540, 720),
            _page(text),
            fontsize=11,
            fontname="helv",
            align=0,
        )
    doc.save(str(path))
    doc.close()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, pages in LECTURES.items():
        path = OUT_DIR / name
        write_pdf(path, pages)
        print(f"wrote {path} ({len(pages)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

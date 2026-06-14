import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# Physical Constants for synthetic data generation
G = 6.67430e-11
EARTH_MASS = 5.972e24
EARTH_RADIUS = 6.371e6

def generate_dataset(n_samples=500):
    """Generates synthetic data representing our physics space"""
    # Masses from 1kg to 1000kg
    masses = np.random.uniform(1, 1000, n_samples)
    # Heights from 0m to 10000m
    heights = np.random.uniform(0, 10000, n_samples)
    
    # Required opposing force to hover (F_req = F_g)
    # F = G * M * m / (r_earth + h)^2
    r_totals = EARTH_RADIUS + heights
    required_forces = G * (EARTH_MASS * masses) / (r_totals ** 2)
    
    X = np.column_stack((masses, heights))
    y = required_forces
    return X, y

# Global model instance
model = None

def train_model():
    """Trains a simple ML model to predict required force."""
    global model
    X, y = generate_dataset()
    # Gravity is non-linear with respect to height, so we use polynomial features
    # even though it's technically a "Linear Regression" model base.
    model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    model.fit(X, y)
    print("AI Model Trained Successfully!")

def predict_required_force(mass, height):
    """Predicts required force. Trains model if not already trained."""
    global model
    if model is None:
        train_model()
    
    # Needs to be a 2D array: [[mass, height]]
    X_input = np.array([[mass, height]])
    prediction = model.predict(X_input)[0]
    
    # Ensure we don't predict negative forces due to polynomial approximation
    return max(0.0, prediction)

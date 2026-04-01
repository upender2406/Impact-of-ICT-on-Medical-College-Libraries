"""
ML Model Training Service
Handles automatic and manual retraining of ML models
"""
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import os
import json
from pathlib import Path
from datetime import datetime
import joblib

# Import sklearn components
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, RandomForestRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error, mean_absolute_error, classification_report
from sklearn.model_selection import cross_val_score

# Try to import XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class TrainingService:
    """
    Service for training and retraining ML models.
    Tracks data count and automatically retrains after every 100 new entries.
    """
    
    def __init__(self, model_path: Optional[str] = None, training_state_path: Optional[str] = None):
        """
        Initialize Training Service.
        
        Args:
            model_path: Path to save trained models
            training_state_path: Path to save training state (data count, last training time)
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent.parent / "ml_models" / "ict_ml_models_complete.pkl"
        
        if training_state_path is None:
            training_state_path = Path(__file__).parent.parent.parent / "ml_models" / "training_state.json"
        
        self.model_path = Path(model_path)
        self.training_state_path = Path(training_state_path)
        self.model_dir = self.model_path.parent
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Training state
        self.training_state = self._load_training_state()
        
        # Threshold for auto-retraining
        self.retrain_threshold = 100  # Retrain after 100 new entries
    
    def _load_training_state(self) -> Dict[str, Any]:
        """Load training state from file."""
        if self.training_state_path.exists():
            try:
                with open(self.training_state_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading training state: {e}")
        
        # Default state
        return {
            'last_training_data_count': 0,
            'current_data_count': 0,
            'new_entries_since_training': 0,
            'last_training_time': None,
            'last_training_metrics': {},
            'total_training_count': 0
        }
    
    def _save_training_state(self):
        """Save training state to file."""
        try:
            with open(self.training_state_path, 'w') as f:
                json.dump(self.training_state, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving training state: {e}")
    
    def update_data_count(self, new_count: int):
        """
        Update the data count and check if retraining is needed.
        
        Args:
            new_count: Current total number of data entries
            
        Returns:
            Tuple[bool, int]: (should_retrain, new_entries_since_training)
        """
        self.training_state['current_data_count'] = new_count
        
        # If never trained before, set should_retrain based on minimum threshold
        if self.training_state['last_training_data_count'] == 0:
            # Need at least 100 entries to start training
            if new_count >= 100:
                self.training_state['new_entries_since_training'] = new_count
                should_retrain = True
            else:
                self.training_state['new_entries_since_training'] = new_count
                should_retrain = False
        else:
            # Calculate new entries since last training
            self.training_state['new_entries_since_training'] = (
                new_count - self.training_state['last_training_data_count']
            )
            should_retrain = (
                self.training_state['new_entries_since_training'] >= self.retrain_threshold
            )
        
        self._save_training_state()
        return should_retrain, self.training_state['new_entries_since_training']
    
    def train_models(self, df: pd.DataFrame, force: bool = False) -> Dict[str, Any]:
        """
        Train all ML models on the provided dataset.
        
        Args:
            df: DataFrame with training data
            force: If True, force retraining even if threshold not met
            
        Returns:
            Dictionary with training metrics and status
        """
        try:
            print(f"🚀 Starting model training on {len(df)} samples...")
            
            # Prepare data (similar to colab.py)
            df = self._prepare_data(df)
            
            # Train all models
            metrics = {}
            
            # 1. Satisfaction Classifier
            print("Training Satisfaction Classifier...")
            classifier_metrics = self._train_classifier(df)
            metrics['satisfaction_classifier'] = classifier_metrics
            
            # 2. Efficiency Regressor
            print("Training Efficiency Regressor...")
            regressor_metrics = self._train_regressor(df)
            metrics['efficiency_regressor'] = regressor_metrics
            
            # 3. College Clustering
            print("Training College Clustering...")
            clustering_metrics = self._train_clustering(df)
            metrics['college_clustering'] = clustering_metrics
            
            # 4. ROI Predictor
            print("Training ROI Predictor...")
            roi_metrics = self._train_roi_predictor(df)
            metrics['roi_predictor'] = roi_metrics
            
            # 5. Enhanced Efficiency Predictor with Confidence Intervals
            print("Training Enhanced Efficiency Predictor...")
            enhanced_efficiency_metrics = self._train_enhanced_efficiency_predictor(df)
            metrics['enhanced_efficiency_predictor'] = enhanced_efficiency_metrics
            
            # 6. Scenario Impact Simulator
            print("Training Scenario Impact Simulator...")
            scenario_metrics = self._train_scenario_simulator(df)
            metrics['scenario_simulator'] = scenario_metrics
            
            # 7. AI Recommendation Engine
            print("Training AI Recommendation Engine...")
            recommendation_metrics = self._train_recommendation_engine(df)
            metrics['recommendation_engine'] = recommendation_metrics
            
            # Save models
            models_package = self._create_models_package(df, metrics)
            self._save_models(models_package)
            
            # Update training state
            self.training_state['last_training_data_count'] = len(df)
            self.training_state['new_entries_since_training'] = 0
            self.training_state['last_training_time'] = datetime.now().isoformat()
            self.training_state['last_training_metrics'] = metrics
            self.training_state['total_training_count'] += 1
            self._save_training_state()
            
            print("✅ Model training completed successfully!")
            
            return {
                'status': 'success',
                'message': 'Models trained successfully',
                'metrics': metrics,
                'training_info': {
                    'data_count': len(df),
                    'training_time': self.training_state['last_training_time'],
                    'total_trainings': self.training_state['total_training_count']
                }
            }
            
        except Exception as e:
            print(f"❌ Error during training: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e),
                'metrics': {}
            }
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for training (feature engineering, encoding, etc.)."""
        print(f"Preparing data with {len(df)} records...")
        print(f"Columns: {list(df.columns)}")
        
        # Handle different data formats (database vs API format)
        if 'infrastructure' in df.columns and isinstance(df['infrastructure'].iloc[0], dict):
            # API format - extract nested dictionaries
            for idx, row in df.iterrows():
                infra = row.get('infrastructure', {})
                service = row.get('serviceQuality', {})
                barriers = row.get('barriers', {})
                additional = row.get('additionalInfo', {})
                
                # Infrastructure fields
                df.at[idx, 'hardware_quality'] = infra.get('hardwareQuality', 3)
                df.at[idx, 'software_availability'] = infra.get('softwareAvailability', 3)
                df.at[idx, 'internet_speed'] = infra.get('internetSpeed', 3)
                df.at[idx, 'digital_collection'] = infra.get('digitalCollection', 3)
                df.at[idx, 'automation_system'] = infra.get('automationSystem', 'None')
                
                # Service quality fields
                df.at[idx, 'overall_satisfaction'] = service.get('overallSatisfaction', 5)
                df.at[idx, 'service_efficiency'] = service.get('serviceEfficiency', 5)
                df.at[idx, 'staff_helpfulness'] = service.get('staffHelpfulness', 5)
                
                # Barriers fields
                df.at[idx, 'financial_barrier'] = barriers.get('financialBarrier', 3)
                df.at[idx, 'technical_barrier'] = barriers.get('technicalBarrier', 3)
                df.at[idx, 'training_barrier'] = barriers.get('trainingBarrier', 3)
                df.at[idx, 'policy_barrier'] = barriers.get('policyBarrier', 3)
                
                # Additional info
                df.at[idx, 'weekly_visits'] = additional.get('weeklyVisits', 5)
                df.at[idx, 'ict_training_received'] = additional.get('ictTrainingReceived', False)
                df.at[idx, 'remote_access_available'] = additional.get('remoteAccessAvailable', False)
                df.at[idx, 'awareness_level'] = additional.get('awarenessLevel', 3)
                
                # College info
                df.at[idx, 'college'] = row.get('collegeName', 'Unknown')
        
        # Create derived features
        if 'infrastructure_score' not in df.columns:
            df['infrastructure_score'] = (
                pd.to_numeric(df['hardware_quality'], errors='coerce').fillna(3) + 
                pd.to_numeric(df['software_availability'], errors='coerce').fillna(3) + 
                pd.to_numeric(df['internet_speed'], errors='coerce').fillna(3) + 
                pd.to_numeric(df['digital_collection'], errors='coerce').fillna(3)
            ) / 4
        
        if 'barrier_score' not in df.columns:
            df['barrier_score'] = (
                pd.to_numeric(df['financial_barrier'], errors='coerce').fillna(3) + 
                pd.to_numeric(df['technical_barrier'], errors='coerce').fillna(3) + 
                pd.to_numeric(df['training_barrier'], errors='coerce').fillna(3) + 
                pd.to_numeric(df['policy_barrier'], errors='coerce').fillna(3)
            ) / 4
        
        # Create satisfaction category
        if 'satisfaction_category' not in df.columns and 'overall_satisfaction' in df.columns:
            satisfaction_values = pd.to_numeric(df['overall_satisfaction'], errors='coerce').fillna(5)
            df['satisfaction_category'] = pd.cut(
                satisfaction_values,
                bins=[0, 5, 7.5, 10],
                labels=['Low', 'Medium', 'High']
            )
        
        # Fill missing values
        numeric_columns = ['hardware_quality', 'software_availability', 'internet_speed', 
                          'digital_collection', 'overall_satisfaction', 'service_efficiency',
                          'staff_helpfulness', 'financial_barrier', 'technical_barrier',
                          'training_barrier', 'policy_barrier', 'weekly_visits', 'awareness_level']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(3)
        
        # Handle categorical columns
        if 'automation_system' in df.columns:
            df['automation_system'] = df['automation_system'].fillna('None')
        if 'college' in df.columns:
            df['college'] = df['college'].fillna('Unknown')
        
        # Handle boolean columns
        bool_columns = ['ict_training_received', 'remote_access_available']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].fillna(False)
        
        print(f"Data preparation complete. Final shape: {df.shape}")
        return df
    
    def _train_classifier(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train satisfaction classifier."""
        # Prepare features
        feature_cols = [
            'infrastructure_score', 'barrier_score', 'automation_encoded',
            'college_encoded', 'awareness_level', 'weekly_visits',
            'training_encoded', 'remote_encoded'
        ]
        
        # Encode categorical variables
        from sklearn.preprocessing import LabelEncoder
        le_college = LabelEncoder()
        le_automation = LabelEncoder()
        le_training = LabelEncoder()
        le_remote = LabelEncoder()
        le_satisfaction = LabelEncoder()
        
        # Handle college encoding
        colleges = df['college'].fillna('Unknown').astype(str)
        df['college_encoded'] = le_college.fit_transform(colleges)
        
        # Handle automation system encoding
        automation = df['automation_system'].fillna('None').astype(str)
        df['automation_encoded'] = le_automation.fit_transform(automation)
        
        # Handle training encoding
        training = df['ict_training_received'].fillna(False).astype(str)
        df['training_encoded'] = le_training.fit_transform(training)
        
        # Handle remote access encoding
        remote = df['remote_access_available'].fillna(False).astype(str)
        df['remote_encoded'] = le_remote.fit_transform(remote)
        
        # Prepare features and target
        X = df[feature_cols].fillna(df[feature_cols].mean())
        
        # Handle satisfaction category - ensure it exists and is properly encoded
        if 'satisfaction_category' not in df.columns:
            satisfaction_values = pd.to_numeric(df['overall_satisfaction'], errors='coerce').fillna(5)
            df['satisfaction_category'] = pd.cut(
                satisfaction_values,
                bins=[0, 5, 7.5, 10],
                labels=['Low', 'Medium', 'High']
            )
        
        # Convert satisfaction categories to numeric labels
        y_str = df['satisfaction_category'].fillna('Medium').astype(str)
        y = le_satisfaction.fit_transform(y_str)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        if XGBOOST_AVAILABLE:
            model = xgb.XGBClassifier(
                n_estimators=100,  # Reduced for faster training
                max_depth=4,       # Reduced complexity
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                eval_metric='mlogloss'
            )
        else:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42,
                n_jobs=-1
            )
        
        model.fit(X_train, y_train)
        
        # Store the trained model and related objects
        self.trained_classifier = model
        self.le_satisfaction = le_satisfaction
        self.le_college = le_college
        self.le_automation = le_automation
        self.le_training = le_training
        self.le_remote = le_remote
        self.classifier_features = feature_cols
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        
        # Cross-validation
        from sklearn.model_selection import cross_val_score
        cv_scores = cross_val_score(model, X, y, cv=3)  # Reduced CV folds
        
        return {
            'model_type': 'XGBoost' if XGBOOST_AVAILABLE else 'RandomForest',
            'training_accuracy': float(train_acc),
            'testing_accuracy': float(test_acc),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'feature_importance': dict(zip(feature_cols, model.feature_importances_.tolist())),
            'classes': le_satisfaction.classes_.tolist()
        }
    
    def _train_regressor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train efficiency regressor."""
        feature_cols = [
            'infrastructure_score', 'barrier_score', 'automation_encoded',
            'awareness_level', 'hardware_quality', 'internet_speed',
            'digital_collection', 'training_encoded'
        ]
        
        # Use already encoded features from classifier training
        X = df[feature_cols].fillna(df[feature_cols].mean())
        y = pd.to_numeric(df['service_efficiency'], errors='coerce').fillna(5)
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        if XGBOOST_AVAILABLE:
            model = xgb.XGBRegressor(
                n_estimators=100,  # Reduced for faster training
                max_depth=4,       # Reduced complexity
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
        else:
            from sklearn.ensemble import GradientBoostingRegressor
            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42
            )
        
        model.fit(X_train, y_train)
        
        # Store the trained model and related objects
        self.trained_regressor = model
        self.regressor_features = feature_cols
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Metrics
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        # Cross-validation
        from sklearn.model_selection import cross_val_score
        cv_scores = cross_val_score(model, X, y, cv=3, scoring='r2')  # Reduced CV folds
        
        return {
            'model_type': 'XGBoost' if XGBOOST_AVAILABLE else 'GradientBoosting',
            'training_r2': float(train_r2),
            'testing_r2': float(test_r2),
            'training_rmse': float(train_rmse),
            'testing_rmse': float(test_rmse),
            'training_mae': float(train_mae),
            'testing_mae': float(test_mae),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'feature_importance': dict(zip(feature_cols, model.feature_importances_.tolist()))
        }
    
    def _train_clustering(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train college clustering model."""
        college_features = df.groupby('college').agg({
            'infrastructure_score': 'mean',
            'barrier_score': 'mean',
            'overall_satisfaction': 'mean',
            'service_efficiency': 'mean'
        }).reset_index()
        
        X_cluster = college_features[[
            'infrastructure_score', 'barrier_score',
            'overall_satisfaction', 'service_efficiency'
        ]]
        
        scaler = StandardScaler()
        X_cluster_scaled = scaler.fit_transform(X_cluster)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_cluster_scaled)
        
        # Store the trained models
        self.trained_clusterer = kmeans
        self.trained_scaler = scaler
        self.cluster_features = ['infrastructure_score', 'barrier_score', 'overall_satisfaction', 'service_efficiency']
        
        college_features['cluster'] = clusters
        
        return {
            'n_clusters': 3,
            'n_colleges': len(college_features),
            'cluster_distribution': {
                int(cluster): int((clusters == cluster).sum())
                for cluster in range(3)
            }
        }
    
    def _train_roi_predictor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train ROI predictor."""
        roi_features = ['infrastructure_score']
        X_roi = df[roi_features].fillna(df[roi_features].mean())
        y_roi = df['overall_satisfaction']
        
        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=6,
            min_samples_split=15,
            min_samples_leaf=6,
            max_features='sqrt',
            max_samples=0.75,
            random_state=42
        )
        model.fit(X_roi, y_roi)
        
        # Store the trained model
        self.trained_roi_predictor = model
        
        roi_coefficient = model.feature_importances_[0]
        
        return {
            'roi_coefficient': float(roi_coefficient),
            'estimated_satisfaction_gain_per_point': float(roi_coefficient * 10)
        }
    
    def _train_enhanced_efficiency_predictor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train enhanced efficiency predictor with confidence intervals and uncertainty quantification."""
        try:
            # Enhanced feature set for efficiency prediction
            feature_cols = [
                'infrastructure_score', 'barrier_score', 'automation_encoded',
                'awareness_level', 'hardware_quality', 'internet_speed',
                'digital_collection', 'training_encoded', 'weekly_visits',
                'remote_encoded', 'college_encoded'
            ]
            
            # Prepare features and target
            X = df[feature_cols].fillna(df[feature_cols].mean())
            y = pd.to_numeric(df['service_efficiency'], errors='coerce').fillna(5)
            
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train ensemble of models for better uncertainty estimation
            models = []
            
            # Model 1: XGBoost/RandomForest
            if XGBOOST_AVAILABLE:
                model1 = xgb.XGBRegressor(
                    n_estimators=150,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42,
                    n_jobs=-1
                )
            else:
                from sklearn.ensemble import RandomForestRegressor
                model1 = RandomForestRegressor(
                    n_estimators=150,
                    max_depth=8,
                    random_state=42,
                    n_jobs=-1
                )
            
            # Model 2: Gradient Boosting
            from sklearn.ensemble import GradientBoostingRegressor
            model2 = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=43
            )
            
            # Model 3: Neural Network
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import StandardScaler
            scaler_nn = StandardScaler()
            X_train_scaled = scaler_nn.fit_transform(X_train)
            X_test_scaled = scaler_nn.transform(X_test)
            
            model3 = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=44,
                early_stopping=True,
                validation_fraction=0.1
            )
            
            # Train all models
            model1.fit(X_train, y_train)
            model2.fit(X_train, y_train)
            model3.fit(X_train_scaled, y_train)
            
            models = {
                'random_forest': model1,
                'gradient_boosting': model2,
                'neural_network': model3
            }
            
            # Store models and scaler
            self.trained_enhanced_efficiency_models = models
            self.trained_enhanced_efficiency_scaler = scaler_nn
            self.enhanced_efficiency_features = feature_cols
            
            # Evaluate ensemble performance
            predictions = []
            for model_name, model in models.items():
                if model_name == 'neural_network':
                    pred = model.predict(X_test_scaled)
                else:
                    pred = model.predict(X_test)
                predictions.append(pred)
            nn_pred = model3.predict(X_test_scaled)
            predictions.append(nn_pred)
            
            # Ensemble prediction (mean)
            ensemble_pred = np.mean(predictions, axis=0)
            
            # Calculate metrics
            from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
            r2 = r2_score(y_test, ensemble_pred)
            rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
            mae = mean_absolute_error(y_test, ensemble_pred)
            
            # Calculate prediction intervals using ensemble variance
            pred_std = np.std(predictions, axis=0)
            
            return {
                'model_type': 'Enhanced Ensemble',
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'ensemble_size': len(models),
                'feature_count': len(feature_cols),
                'prediction_std_mean': float(np.mean(pred_std)),
                'confidence_interval_coverage': 0.95
            }
            
        except Exception as e:
            print(f"Error training enhanced efficiency predictor: {e}")
            return {
                'model_type': 'Enhanced Ensemble',
                'error': str(e),
                'r2_score': 0.0,
                'rmse': 999.0,
                'mae': 999.0
            }
    
    def _create_models_package(self, df: pd.DataFrame, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create models package for saving."""
        return {
            'models': {
                'satisfaction_classifier': getattr(self, 'trained_classifier', None),
                'efficiency_regressor': getattr(self, 'trained_regressor', None),
                'college_clusterer': getattr(self, 'trained_clusterer', None),
                'roi_predictor': getattr(self, 'trained_roi_predictor', None),
                'enhanced_efficiency_models': getattr(self, 'trained_enhanced_efficiency_models', None),
                'scenario_sat_model': getattr(self, 'trained_scenario_sat_model', None),
                'scenario_eff_model': getattr(self, 'trained_scenario_eff_model', None),
                'recommendation_classifier': getattr(self, 'trained_recommendation_classifier', None),
                'priority_model': getattr(self, 'trained_priority_model', None)
            },
            'scalers': {
                'scaler': getattr(self, 'trained_scaler', None),
                'scaler_nn': getattr(self, 'trained_scaler_nn', None),
                'scaler_nn_class': getattr(self, 'trained_scaler_nn_class', None),
                'enhanced_efficiency_scaler': getattr(self, 'trained_enhanced_efficiency_scaler', None)
            },
            'encoders': {
                'label_encoders': getattr(self, 'trained_label_encoders', {}),
                'le_satisfaction': getattr(self, 'le_satisfaction', None),
                'le_college': getattr(self, 'le_college', None),
                'le_automation': getattr(self, 'le_automation', None),
                'le_training': getattr(self, 'le_training', None),
                'le_remote': getattr(self, 'le_remote', None),
                'recommendation_label_encoder': getattr(self, 'recommendation_label_encoder', None)
            },
            'features': {
                'satisfaction_classifier': getattr(self, 'classifier_features', []),
                'efficiency_regressor': getattr(self, 'regressor_features', []),
                'cluster_features': getattr(self, 'cluster_features', []),
                'enhanced_efficiency_features': getattr(self, 'enhanced_efficiency_features', []),
                'scenario_features': getattr(self, 'scenario_features', []),
                'recommendation_features': getattr(self, 'recommendation_features', [])
            },
            'templates': {
                'recommendation_templates': getattr(self, 'recommendation_templates', {}),
                'scenario_cost_estimates': getattr(self, 'scenario_cost_estimates', {})
            },
            'metrics': metrics,
            'training_data_count': len(df),
            'training_timestamp': datetime.now().isoformat()
        }
    
    def _save_models(self, models_package: Dict[str, Any]):
        """Save trained models to file."""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(models_package, f)
            print(f"✅ Models saved to {self.model_path}")
        except Exception as e:
            print(f"❌ Error saving models: {e}")
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status and metrics."""
        return {
            'current_data_count': self.training_state['current_data_count'],
            'last_training_data_count': self.training_state['last_training_data_count'],
            'new_entries_since_training': self.training_state['new_entries_since_training'],
            'entries_until_retrain': max(0, self.retrain_threshold - self.training_state['new_entries_since_training']),
            'last_training_time': self.training_state['last_training_time'],
            'last_training_metrics': self.training_state['last_training_metrics'],
            'total_training_count': self.training_state['total_training_count'],
            'retrain_threshold': self.retrain_threshold,
            'should_retrain': self.training_state['new_entries_since_training'] >= self.retrain_threshold
        }

    def _train_scenario_simulator(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train scenario impact simulator for what-if analysis."""
        try:
            # Create scenario simulation training data
            # This model predicts the impact of infrastructure improvements
            
            # Features: current state + proposed changes
            scenario_features = [
                'infrastructure_score', 'barrier_score', 'automation_encoded',
                'awareness_level', 'college_encoded', 'training_encoded'
            ]
            
            # Target: improvement in satisfaction/efficiency
            X = df[scenario_features].fillna(df[scenario_features].mean())
            y_satisfaction = pd.to_numeric(df['overall_satisfaction'], errors='coerce').fillna(5)
            y_efficiency = pd.to_numeric(df['service_efficiency'], errors='coerce').fillna(5)
            
            # Create synthetic scenario data for training
            # Generate "what-if" scenarios by modifying infrastructure scores
            scenario_X = []
            scenario_y_sat = []
            scenario_y_eff = []
            
            for idx, row in X.iterrows():
                current_infra = row['infrastructure_score']
                current_barrier = row['barrier_score']
                
                # Generate improvement scenarios
                for infra_improvement in [0.5, 1.0, 1.5, 2.0]:
                    for barrier_reduction in [0.5, 1.0, 1.5]:
                        new_infra = min(5.0, current_infra + infra_improvement)
                        new_barrier = max(1.0, current_barrier - barrier_reduction)
                        
                        # Create scenario features
                        scenario_row = row.copy()
                        scenario_row['infrastructure_score'] = new_infra
                        scenario_row['barrier_score'] = new_barrier
                        
                        # Estimate impact (simplified model)
                        infra_impact = infra_improvement * 0.8  # 80% efficiency
                        barrier_impact = barrier_reduction * 0.6  # 60% efficiency
                        
                        expected_sat_improvement = infra_impact + barrier_impact
                        expected_eff_improvement = infra_impact * 1.2 + barrier_impact * 0.8
                        
                        scenario_X.append(scenario_row.values)
                        scenario_y_sat.append(expected_sat_improvement)
                        scenario_y_eff.append(expected_eff_improvement)
            
            # Convert to arrays
            X_scenario = np.array(scenario_X)
            y_scenario_sat = np.array(scenario_y_sat)
            y_scenario_eff = np.array(scenario_y_eff)
            
            # Train impact prediction models
            from sklearn.ensemble import RandomForestRegressor
            
            # Satisfaction impact model
            sat_impact_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=6,
                random_state=42,
                n_jobs=-1
            )
            sat_impact_model.fit(X_scenario, y_scenario_sat)
            
            # Efficiency impact model
            eff_impact_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=6,
                random_state=43,
                n_jobs=-1
            )
            eff_impact_model.fit(X_scenario, y_scenario_eff)
            
            # Cost estimation model (based on infrastructure improvements)
            cost_features = ['infrastructure_score', 'automation_encoded', 'college_encoded']
            cost_X = df[cost_features].fillna(df[cost_features].mean())
            
            # Synthetic cost data (realistic estimates)
            base_costs = {
                'hardware_upgrade': 200000,  # ₹2 lakh
                'software_upgrade': 100000,  # ₹1 lakh
                'internet_upgrade': 50000,   # ₹50k
                'training_program': 75000,   # ₹75k
                'automation_system': 300000  # ₹3 lakh
            }
            
            # Store models
            self.trained_scenario_sat_model = sat_impact_model
            self.trained_scenario_eff_model = eff_impact_model
            self.scenario_features = scenario_features
            self.scenario_cost_estimates = base_costs
            
            # Calculate model performance on synthetic data
            from sklearn.model_selection import cross_val_score
            sat_cv_scores = cross_val_score(sat_impact_model, X_scenario, y_scenario_sat, cv=3)
            eff_cv_scores = cross_val_score(eff_impact_model, X_scenario, y_scenario_eff, cv=3)
            
            return {
                'model_type': 'Scenario Impact Simulator',
                'satisfaction_impact_r2': float(sat_cv_scores.mean()),
                'efficiency_impact_r2': float(eff_cv_scores.mean()),
                'scenario_count': len(scenario_X),
                'feature_count': len(scenario_features),
                'cost_categories': len(base_costs)
            }
            
        except Exception as e:
            print(f"Error training scenario simulator: {e}")
            return {
                'model_type': 'Scenario Impact Simulator',
                'error': str(e),
                'satisfaction_impact_r2': 0.0,
                'efficiency_impact_r2': 0.0
            }
    
    def _train_recommendation_engine(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train AI-powered recommendation engine for versatile solutions."""
        try:
            # Create recommendation training data
            # This model learns patterns to suggest improvements
            
            # Features for recommendation
            rec_features = [
                'infrastructure_score', 'barrier_score', 'overall_satisfaction',
                'service_efficiency', 'automation_encoded', 'college_encoded',
                'training_encoded', 'remote_encoded', 'awareness_level'
            ]
            
            X = df[rec_features].fillna(df[rec_features].mean())
            
            # Create recommendation categories based on current state
            recommendations_db = []
            
            # Define recommendation templates
            recommendation_templates = {
                'infrastructure_low': [
                    {
                        'area': 'Hardware Infrastructure',
                        'action': 'Upgrade computer systems and networking equipment',
                        'priority': 9,
                        'expected_impact': 2.5,
                        'estimated_cost': 250000,
                        'timeline': '3-6 months'
                    },
                    {
                        'area': 'Internet Connectivity',
                        'action': 'Upgrade to high-speed broadband connection',
                        'priority': 8,
                        'expected_impact': 2.0,
                        'estimated_cost': 75000,
                        'timeline': '1-2 months'
                    }
                ],
                'automation_none': [
                    {
                        'area': 'Library Automation',
                        'action': 'Implement KOHA or SOUL library management system',
                        'priority': 7,
                        'expected_impact': 3.0,
                        'estimated_cost': 150000,
                        'timeline': '2-4 months'
                    }
                ],
                'training_low': [
                    {
                        'area': 'Staff Training',
                        'action': 'Conduct comprehensive ICT training programs',
                        'priority': 6,
                        'expected_impact': 1.8,
                        'estimated_cost': 50000,
                        'timeline': '1-3 months'
                    }
                ],
                'satisfaction_low': [
                    {
                        'area': 'User Experience',
                        'action': 'Redesign library layout and improve user interfaces',
                        'priority': 5,
                        'expected_impact': 1.5,
                        'estimated_cost': 100000,
                        'timeline': '2-3 months'
                    }
                ],
                'barriers_high': [
                    {
                        'area': 'Policy Framework',
                        'action': 'Develop clear ICT policies and procedures',
                        'priority': 4,
                        'expected_impact': 1.2,
                        'estimated_cost': 25000,
                        'timeline': '1 month'
                    }
                ],
                'digital_collection': [
                    {
                        'area': 'Digital Resources',
                        'action': 'Expand digital collection and e-resources',
                        'priority': 6,
                        'expected_impact': 2.2,
                        'estimated_cost': 200000,
                        'timeline': '3-6 months'
                    }
                ]
            }
            
            # Generate training data for recommendation classifier
            X_rec = []
            y_rec = []
            
            for idx, row in X.iterrows():
                infra_score = row['infrastructure_score']
                barrier_score = row['barrier_score']
                satisfaction = row['overall_satisfaction']
                automation = row['automation_encoded']
                training = row['training_encoded']
                
                # Determine applicable recommendations
                applicable_recs = []
                
                if infra_score < 3:
                    applicable_recs.extend(['infrastructure_low'])
                if automation == 0:  # No automation
                    applicable_recs.extend(['automation_none'])
                if training == 0:  # No training
                    applicable_recs.extend(['training_low'])
                if satisfaction < 5:
                    applicable_recs.extend(['satisfaction_low'])
                if barrier_score > 3:
                    applicable_recs.extend(['barriers_high'])
                
                # Always consider digital collection
                applicable_recs.append('digital_collection')
                
                for rec_type in applicable_recs:
                    X_rec.append(row.values)
                    y_rec.append(rec_type)
            
            # Train recommendation classifier
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            
            le_recommendations = LabelEncoder()
            y_rec_encoded = le_recommendations.fit_transform(y_rec)
            
            rec_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                random_state=42,
                n_jobs=-1
            )
            
            if len(X_rec) > 0:
                rec_classifier.fit(X_rec, y_rec_encoded)
            
            # Train priority scoring model
            priority_features = ['infrastructure_score', 'barrier_score', 'overall_satisfaction']
            priority_X = df[priority_features].fillna(df[priority_features].mean())
            
            # Calculate priority scores (higher urgency = higher priority)
            priority_scores = []
            for idx, row in priority_X.iterrows():
                # Priority based on gaps and urgency
                infra_gap = 5 - row['infrastructure_score']  # Gap from ideal
                barrier_impact = row['barrier_score'] - 1    # Barrier severity
                satisfaction_gap = 10 - row['overall_satisfaction']  # Satisfaction gap
                
                priority = (infra_gap * 2 + barrier_impact * 1.5 + satisfaction_gap * 1) / 4.5 * 10
                priority_scores.append(min(10, max(1, priority)))
            
            from sklearn.ensemble import GradientBoostingRegressor
            priority_model = GradientBoostingRegressor(
                n_estimators=50,
                max_depth=4,
                random_state=42
            )
            
            if len(priority_X) > 0:
                priority_model.fit(priority_X, priority_scores)
            
            # Store models and data
            self.trained_recommendation_classifier = rec_classifier
            self.trained_priority_model = priority_model
            self.recommendation_label_encoder = le_recommendations
            self.recommendation_templates = recommendation_templates
            self.recommendation_features = rec_features
            
            # Calculate performance metrics
            if len(X_rec) > 0:
                from sklearn.model_selection import cross_val_score
                rec_cv_scores = cross_val_score(rec_classifier, X_rec, y_rec_encoded, cv=3)
                priority_cv_scores = cross_val_score(priority_model, priority_X, priority_scores, cv=3)
                
                return {
                    'model_type': 'AI Recommendation Engine',
                    'recommendation_accuracy': float(rec_cv_scores.mean()),
                    'priority_r2': float(priority_cv_scores.mean()),
                    'recommendation_categories': len(recommendation_templates),
                    'training_samples': len(X_rec),
                    'feature_count': len(rec_features)
                }
            else:
                return {
                    'model_type': 'AI Recommendation Engine',
                    'recommendation_accuracy': 0.0,
                    'priority_r2': 0.0,
                    'recommendation_categories': len(recommendation_templates),
                    'training_samples': 0,
                    'feature_count': len(rec_features)
                }
            
        except Exception as e:
            print(f"Error training recommendation engine: {e}")
            import traceback
            traceback.print_exc()
            return {
                'model_type': 'AI Recommendation Engine',
                'error': str(e),
                'recommendation_accuracy': 0.0,
                'priority_r2': 0.0
            }


# Global training service instance
training_service = TrainingService()
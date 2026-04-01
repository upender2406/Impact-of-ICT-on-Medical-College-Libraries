import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import os
from pathlib import Path


class MLService:
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ML Service with pre-trained models.
        
        Args:
            model_path: Path to the pickle file containing models.
                       Defaults to ml_models/ict_ml_models.pkl
        """
        if model_path is None:
            # Default path relative to backend directory
            model_path = Path(__file__).parent.parent.parent / "ml_models" / "ict_ml_models_complete.pkl"
        
        self.model_path = model_path
        self.models = None
        self.satisfaction_classifier = None
        self.efficiency_regressor = None
        self.college_clusters = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        
        # Models set by load_models()
        self.college_clusterer = None
        self.roi_predictor = None
        self.enhanced_efficiency_models = None
        self.scenario_sat_model = None
        self.scenario_eff_model = None
        self.recommendation_classifier = None
        self.priority_model = None
        
        # Scalers
        self.scaler_nn = None
        self.scaler_nn_class = None
        self.enhanced_efficiency_scaler = None
        
        # Encoders
        self.le_satisfaction = None
        self.le_college = None
        self.le_automation = None
        self.le_training = None
        self.le_remote = None
        self.recommendation_label_encoder = None
        
        # Feature lists
        self.feature_cols_class = []
        self.feature_cols_reg = []
        self.cluster_features = []
        self.enhanced_efficiency_features = []
        self.scenario_features = []
        self.recommendation_features = []
        
        # Templates and reference data
        self.recommendation_templates = {}
        self.scenario_cost_estimates = {}
        self.reference_data = {}
        
        # Try to load models if file exists
        if os.path.exists(model_path):
            self.load_models()
        else:
            print(f"Warning: Model file not found at {model_path}. Using mock predictions.")
    
    def load_models(self):
        """Load ML models from pickle file."""
        try:
            with open(self.model_path, 'rb') as f:
                self.models = pickle.load(f)
            
            # Extract models from the new structure
            models_dict = self.models.get('models', {})
            self.satisfaction_classifier = models_dict.get('satisfaction_classifier')
            self.efficiency_regressor = models_dict.get('efficiency_regressor')
            self.college_clusterer = models_dict.get('college_clusterer')
            self.roi_predictor = models_dict.get('roi_predictor')
            
            # New enhanced models
            self.enhanced_efficiency_models = models_dict.get('enhanced_efficiency_models')
            self.scenario_sat_model = models_dict.get('scenario_sat_model')
            self.scenario_eff_model = models_dict.get('scenario_eff_model')
            self.recommendation_classifier = models_dict.get('recommendation_classifier')
            self.priority_model = models_dict.get('priority_model')
            
            # Extract scalers
            scalers_dict = self.models.get('scalers', {})
            self.scaler = scalers_dict.get('scaler')
            self.scaler_nn = scalers_dict.get('scaler_nn')
            self.scaler_nn_class = scalers_dict.get('scaler_nn_class')
            self.enhanced_efficiency_scaler = scalers_dict.get('enhanced_efficiency_scaler')
            
            # Extract encoders
            encoders_dict = self.models.get('encoders', {})
            self.label_encoders = encoders_dict.get('label_encoders', {})
            self.le_satisfaction = encoders_dict.get('le_satisfaction')
            self.le_college = encoders_dict.get('le_college')
            self.le_automation = encoders_dict.get('le_automation')
            self.le_training = encoders_dict.get('le_training')
            self.le_remote = encoders_dict.get('le_remote')
            self.recommendation_label_encoder = encoders_dict.get('recommendation_label_encoder')
            
            # Extract feature lists
            features_dict = self.models.get('features', {})
            self.feature_cols_class = features_dict.get('satisfaction_classifier', [])
            self.feature_cols_reg = features_dict.get('efficiency_regressor', [])
            self.cluster_features = features_dict.get('cluster_features', [])
            self.enhanced_efficiency_features = features_dict.get('enhanced_efficiency_features', [])
            self.scenario_features = features_dict.get('scenario_features', [])
            self.recommendation_features = features_dict.get('recommendation_features', [])
            
            # Extract templates and reference data
            templates_dict = self.models.get('templates', {})
            self.recommendation_templates = templates_dict.get('recommendation_templates', {})
            self.scenario_cost_estimates = templates_dict.get('scenario_cost_estimates', {})
            
            print("ML models loaded successfully!")
            print(f"   - Satisfaction Classifier: {'OK' if self.satisfaction_classifier else 'MISSING'}")
            print(f"   - Efficiency Regressor: {'OK' if self.efficiency_regressor else 'MISSING'}")
            print(f"   - College Clusterer: {'OK' if self.college_clusterer else 'MISSING'}")
            print(f"   - Enhanced Efficiency Models: {'OK' if self.enhanced_efficiency_models else 'MISSING'}")
            print(f"   - Scenario Models: {'OK' if self.scenario_sat_model and self.scenario_eff_model else 'MISSING'}")
            print(f"   - Recommendation Engine: {'OK' if self.recommendation_classifier else 'MISSING'}")
            print(f"   - Classifier Features: {len(self.feature_cols_class)}")
            print(f"   - Regressor Features: {len(self.feature_cols_reg)}")
        except Exception as e:
            print(f"Error loading models: {e}")
            import traceback
            traceback.print_exc()
            self.models = None
    
    def _prepare_features_classifier(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Prepare features for satisfaction classifier prediction.
        Uses the exact feature list from the trained model.
        
        Args:
            features: Dictionary containing feature values
            
        Returns:
            numpy array of prepared features in correct order
        """
        if self.models is None or not self.feature_cols_class:
            # Fallback: return minimal features
            return np.array([[features.get('infrastructure_score', 3),
                            features.get('barrier_score', 3),
                            features.get('awareness_level', 5),
                            0, 0, 0, 0, 0]])
        
        # Get feature list from model package
        feature_values = []
        
        for feature_name in self.feature_cols_class:
            if feature_name == 'infrastructure_score':
                feature_values.append(features.get('infrastructure_score', 3.0))
            elif feature_name == 'barrier_score':
                feature_values.append(features.get('barrier_score', 3.0))
            elif feature_name == 'automation_encoded':
                # Encode automation system
                automation = features.get('automation_system', 'None')
                le_automation = self.label_encoders.get('automation')
                if le_automation:
                    try:
                        feature_values.append(le_automation.transform([automation])[0])
                    except:
                        # Fallback if value not in encoder
                        automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                        feature_values.append(automation_map.get(automation, 0))
                else:
                    automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                    feature_values.append(automation_map.get(automation, 0))
            elif feature_name == 'college_encoded':
                # Encode college
                college_id = features.get('college_id', '1')
                le_college = self.label_encoders.get('college')
                if le_college:
                    try:
                        # Try to get college name from reference data
                        college_list = self.reference_data.get('college_list', [])
                        if college_list and str(college_id).isdigit():
                            idx = int(college_id) - 1
                            if 0 <= idx < len(college_list):
                                college_name = college_list[idx]
                                feature_values.append(le_college.transform([college_name])[0])
                            else:
                                feature_values.append(0)
                        else:
                            feature_values.append(int(college_id) if str(college_id).isdigit() else 0)
                    except:
                        feature_values.append(int(college_id) if str(college_id).isdigit() else 0)
                else:
                    feature_values.append(int(college_id) if str(college_id).isdigit() else 0)
            elif feature_name == 'awareness_level':
                feature_values.append(features.get('awareness_level', 3))
            elif feature_name == 'weekly_visits':
                feature_values.append(features.get('weekly_visits', 5))
            elif feature_name == 'training_encoded':
                # Encode training (Yes/No)
                training = features.get('ict_training_received', False)
                le_training = self.label_encoders.get('training')
                if le_training:
                    try:
                        training_str = 'Yes' if training else 'No'
                        feature_values.append(le_training.transform([training_str])[0])
                    except:
                        feature_values.append(1 if training else 0)
                else:
                    feature_values.append(1 if training else 0)
            elif feature_name == 'remote_encoded':
                # Encode remote access (Yes/No)
                remote = features.get('remote_access_available', False)
                le_remote = self.label_encoders.get('remote')
                if le_remote:
                    try:
                        remote_str = 'Yes' if remote else 'No'
                        feature_values.append(le_remote.transform([remote_str])[0])
                    except:
                        feature_values.append(1 if remote else 0)
                else:
                    feature_values.append(1 if remote else 0)
            else:
                # Default value for unknown features
                feature_values.append(0)
        
        # Convert to numpy array and reshape
        X = np.array(feature_values).reshape(1, -1)
        return X
    
    def _prepare_features_regressor(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Prepare features for efficiency regressor prediction.
        Uses the exact feature list from the trained model.
        
        Args:
            features: Dictionary containing feature values
            
        Returns:
            numpy array of prepared features in correct order
        """
        if self.models is None or not self.feature_cols_reg:
            # Fallback: return minimal features
            return np.array([[features.get('infrastructure_score', 3),
                            features.get('barrier_score', 3),
                            features.get('awareness_level', 5),
                            3.0, 3.0, 3.0, 0]])
        
        # Get feature list from model package
        feature_values = []
        
        for feature_name in self.feature_cols_reg:
            if feature_name == 'infrastructure_score':
                feature_values.append(features.get('infrastructure_score', 3.0))
            elif feature_name == 'barrier_score':
                feature_values.append(features.get('barrier_score', 3.0))
            elif feature_name == 'automation_encoded':
                # Encode automation system
                automation = features.get('automation_system', 'None')
                le_automation = self.label_encoders.get('automation')
                if le_automation:
                    try:
                        feature_values.append(le_automation.transform([automation])[0])
                    except:
                        automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                        feature_values.append(automation_map.get(automation, 0))
                else:
                    automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                    feature_values.append(automation_map.get(automation, 0))
            elif feature_name == 'awareness_level':
                feature_values.append(features.get('awareness_level', 3))
            elif feature_name == 'hardware_quality':
                feature_values.append(features.get('hardware_quality', features.get('infrastructure_score', 3.0)))
            elif feature_name == 'internet_speed':
                feature_values.append(features.get('internet_speed', features.get('infrastructure_score', 3.0)))
            elif feature_name == 'digital_collection':
                feature_values.append(features.get('digital_collection', features.get('infrastructure_score', 3.0)))
            elif feature_name == 'training_encoded':
                # Encode training (Yes/No)
                training = features.get('ict_training_received', False)
                le_training = self.label_encoders.get('training')
                if le_training:
                    try:
                        training_str = 'Yes' if training else 'No'
                        feature_values.append(le_training.transform([training_str])[0])
                    except:
                        feature_values.append(1 if training else 0)
                else:
                    feature_values.append(1 if training else 0)
            else:
                # Default value for unknown features
                feature_values.append(0)
        
        # Convert to numpy array and reshape
        X = np.array(feature_values).reshape(1, -1)
        return X
    
    def predict_satisfaction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict satisfaction level with confidence.
        
        Args:
            features: Dictionary containing feature values
            
        Returns:
            Dictionary with prediction, confidence, probabilities, and feature importance
        """
        if self.satisfaction_classifier is None:
            # Mock prediction
            return {
                'prediction': 'Medium',
                'confidence': 0.75,
                'probabilities': {
                    'Low': 0.15,
                    'Medium': 0.75,
                    'High': 0.10
                },
                'feature_importance': [
                    {'feature': 'Infrastructure Score', 'importance': 0.35},
                    {'feature': 'Barrier Score', 'importance': 0.25},
                    {'feature': 'Awareness Level', 'importance': 0.20},
                    {'feature': 'Automation System', 'importance': 0.15},
                    {'feature': 'College', 'importance': 0.05},
                ]
            }
        
        try:
            # Prepare features using the correct feature list from model
            X = self._prepare_features_classifier(features)
            
            # Predict
            prediction = self.satisfaction_classifier.predict(X)[0]
            probabilities = self.satisfaction_classifier.predict_proba(X)[0]
            
            # Handle XGBoostWrapper or direct predictions
            # If prediction is already a string (from XGBoostWrapper), use it directly
            if isinstance(prediction, str):
                prediction_label = prediction
            else:
                # Map numeric prediction to category
                categories = ['Low', 'Medium', 'High']
                prediction_label = categories[prediction] if isinstance(prediction, (int, np.integer)) and prediction < len(categories) else str(prediction)
            
            # Get feature importance if available
            feature_importance = self._get_feature_importance()
            
            return {
                'prediction': prediction_label,
                'confidence': float(max(probabilities)),
                'probabilities': {
                    'Low': float(probabilities[0]) if len(probabilities) > 0 else 0.0,
                    'Medium': float(probabilities[1]) if len(probabilities) > 1 else 0.0,
                    'High': float(probabilities[2]) if len(probabilities) > 2 else 0.0,
                },
                'feature_importance': feature_importance
            }
        except Exception as e:
            print(f"Error in satisfaction prediction: {e}")
            import traceback
            traceback.print_exc()
            # Return mock prediction on error
            return {
                'prediction': 'Medium',
                'confidence': 0.75,
                'probabilities': {'Low': 0.15, 'Medium': 0.75, 'High': 0.10},
                'feature_importance': []
            }
    
    def predict_efficiency(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict service efficiency score using enhanced models if available.
        
        Args:
            features: Dictionary containing feature values
            
        Returns:
            Dictionary with predicted score, confidence interval, and improvement potential
        """
        # Try enhanced efficiency models first
        if self.enhanced_efficiency_models:
            try:
                # Prepare features for enhanced models
                X = self._prepare_features_enhanced_efficiency(features)
                
                # Get predictions from all models in the ensemble
                predictions = []
                for model_name, model in self.enhanced_efficiency_models.items():
                    if model:
                        if model_name == 'neural_network':
                            # Neural network needs scaled features
                            if self.enhanced_efficiency_scaler:
                                X_scaled = self.enhanced_efficiency_scaler.transform(X)
                                pred = model.predict(X_scaled)[0]
                            else:
                                pred = model.predict(X)[0]
                        else:
                            pred = model.predict(X)[0]
                        predictions.append(float(pred))
                
                if predictions:
                    # Ensemble prediction (average)
                    prediction = sum(predictions) / len(predictions)
                    
                    # Calculate confidence interval based on model variance
                    std_error = np.std(predictions) if len(predictions) > 1 else 1.0
                    confidence_interval = {
                        'lower': float(max(1, prediction - 1.96 * std_error)),
                        'upper': float(min(10, prediction + 1.96 * std_error))
                    }
                    
                    # Calculate improvement potential
                    improvement_potential = max(0, 10 - prediction)
                    
                    # Generate enhanced suggestions
                    suggestions = self._generate_enhanced_suggestions(features, prediction)
                    
                    return {
                        'predicted_score': float(prediction),
                        'confidence_interval': confidence_interval,
                        'improvement_potential': float(improvement_potential),
                        'suggestions': suggestions
                    }
            except Exception as e:
                print(f"Error with enhanced efficiency models: {e}")
        
        # Fallback to original efficiency regressor
        if self.efficiency_regressor is None:
            # Mock prediction
            base_score = features.get('infrastructure_score', 3) * 2
            return {
                'predicted_score': float(base_score),
                'confidence_interval': {
                    'lower': float(base_score - 1.0),
                    'upper': float(base_score + 1.0)
                },
                'improvement_potential': float(10 - base_score),
                'suggestions': [
                    'Improve internet connectivity',
                    'Provide ICT training to staff',
                    'Upgrade hardware infrastructure',
                    'Implement automation system'
                ]
            }
        
        try:
            # Prepare features using the correct feature list from model
            X = self._prepare_features_regressor(features)
            
            # Predict
            prediction = self.efficiency_regressor.predict(X)[0]
            
            # Ensure prediction is a float
            prediction = float(prediction)
            
            # Calculate confidence interval (simplified)
            std_error = 1.0  # This should come from the model if available
            confidence_interval = {
                'lower': float(max(1, prediction - 1.96 * std_error)),
                'upper': float(min(10, prediction + 1.96 * std_error))
            }
            
            # Calculate improvement potential
            improvement_potential = max(0, 10 - prediction)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(features, prediction)
            
            return {
                'predicted_score': prediction,
                'confidence_interval': confidence_interval,
                'improvement_potential': float(improvement_potential),
                'suggestions': suggestions
            }
        except Exception as e:
            print(f"Error in efficiency prediction: {e}")
            import traceback
            traceback.print_exc()
            # Return mock prediction on error
            base_score = features.get('infrastructure_score', 3) * 2
            return {
                'predicted_score': float(base_score),
                'confidence_interval': {'lower': float(base_score - 1.0), 'upper': float(base_score + 1.0)},
                'improvement_potential': float(10 - base_score),
                'suggestions': ['Improve internet connectivity', 'Provide ICT training to staff']
            }
    
    def simulate_scenario(self, current: Dict[str, Any], proposed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate impact of proposed changes using enhanced scenario models.
        
        Args:
            current: Current state features
            proposed: Proposed state features
            
        Returns:
            Dictionary with simulation results
        """
        # Try enhanced scenario models first
        if self.scenario_sat_model and self.scenario_eff_model:
            try:
                # Prepare features for scenario models
                current_X = self._prepare_features_scenario(current)
                proposed_X = self._prepare_features_scenario(proposed)
                
                # Predict satisfaction impact
                sat_impact = self.scenario_sat_model.predict(proposed_X)[0]
                current_sat = current.get('overall_satisfaction', 5)
                predicted_sat = min(10, max(1, current_sat + sat_impact))
                
                # Predict efficiency impact
                eff_impact = self.scenario_eff_model.predict(proposed_X)[0]
                current_eff = current.get('service_efficiency', 5)
                predicted_eff = min(10, max(1, current_eff + eff_impact))
                
                # Calculate improvements
                sat_improvement = predicted_sat - current_sat
                eff_improvement = predicted_eff - current_eff
                overall_improvement = (sat_improvement + eff_improvement) / 2
                
                # Calculate percentage improvement
                current_avg = (current_sat + current_eff) / 2
                improvement_percentage = (overall_improvement / current_avg) * 100 if current_avg > 0 else 0
                
                # Enhanced cost estimation
                cost = self._estimate_enhanced_cost(current, proposed)
                
                # Enhanced ROI calculation
                roi = self._calculate_enhanced_roi(overall_improvement, cost)
                
                # Enhanced timeline estimation
                timeline = self._estimate_enhanced_timeline(current, proposed)
                
                return {
                    'current_score': float(current_avg),
                    'predicted_score': float((predicted_sat + predicted_eff) / 2),
                    'improvement': float(overall_improvement),
                    'improvement_percentage': float(improvement_percentage),
                    'estimated_cost': float(cost),
                    'roi': float(roi),
                    'timeline_months': int(timeline)
                }
                
            except Exception as e:
                print(f"Error with enhanced scenario models: {e}")
        
        # Fallback to original method
        current_pred = self.predict_efficiency(current)
        proposed_pred = self.predict_efficiency(proposed)
        
        improvement = proposed_pred['predicted_score'] - current_pred['predicted_score']
        improvement_percentage = (improvement / current_pred['predicted_score']) * 100 if current_pred['predicted_score'] > 0 else 0
        
        # Estimate cost based on improvements
        cost = self._estimate_cost(current, proposed)
        roi = improvement / cost if cost > 0 else 0
        
        # Estimate timeline
        timeline = self._estimate_timeline(proposed)
        
        return {
            'current_score': current_pred['predicted_score'],
            'predicted_score': proposed_pred['predicted_score'],
            'improvement': improvement,
            'improvement_percentage': improvement_percentage,
            'estimated_cost': cost,
            'roi': roi,
            'timeline_months': timeline
        }
    
    def get_recommendations(self, college_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate AI-powered recommendations using the trained recommendation engine.
        
        Args:
            college_data: College-specific data
            
        Returns:
            List of recommendations sorted by priority
        """
        # Use the new AI recommendation engine
        return self.get_ai_recommendations(college_data)
    
    def _get_feature_importance(self) -> List[Dict[str, Any]]:
        """Get feature importance from model."""
        if self.satisfaction_classifier is None:
            return []
        
        # Try to get feature importances
        try:
            # Handle XGBoostWrapper
            if hasattr(self.satisfaction_classifier, 'feature_importances_'):
                importances = self.satisfaction_classifier.feature_importances_
            elif hasattr(self.satisfaction_classifier, 'model') and hasattr(self.satisfaction_classifier.model, 'feature_importances_'):
                importances = self.satisfaction_classifier.model.feature_importances_
            else:
                return []
            
            # Use feature names from model package
            feature_names = self.feature_cols_class if self.feature_cols_class else []
            
            if len(feature_names) != len(importances):
                # Fallback: use generic names
                feature_names = [f'Feature_{i}' for i in range(len(importances))]
            
            return [
                {'feature': name, 'importance': float(imp)}
                for name, imp in zip(feature_names, importances)
            ]
        except Exception as e:
            print(f"Warning: Could not extract feature importance: {e}")
            return []
    
    def _generate_suggestions(self, features: Dict[str, Any], current_score: float) -> List[str]:
        """Generate improvement suggestions based on features and current score."""
        suggestions = []
        
        if features.get('infrastructure_score', 3) < 3:
            suggestions.append('Improve hardware and software infrastructure')
        
        if features.get('barrier_score', 3) > 3:
            suggestions.append('Address financial and technical barriers')
        
        if features.get('automation_system') == 'None':
            suggestions.append('Consider implementing an automation system (KOHA or SOUL)')
        
        if features.get('awareness_level', 5) < 5:
            suggestions.append('Increase ICT awareness through training programs')
        
        if current_score < 5:
            suggestions.append('Focus on improving overall service efficiency')
        
        return suggestions if suggestions else ['Continue current practices and monitor progress']
    
    def _estimate_cost(self, current: Dict[str, Any], proposed: Dict[str, Any]) -> float:
        """Estimate cost of proposed improvements."""
        cost = 0.0
        
        infra_diff = proposed.get('infrastructure_score', 3) - current.get('infrastructure_score', 3)
        if infra_diff > 0:
            cost += infra_diff * 100000  # 1 lakh per point improvement
        
        barrier_diff = current.get('barrier_score', 3) - proposed.get('barrier_score', 3)
        if barrier_diff > 0:
            cost += barrier_diff * 50000  # 50k per point reduction
        
        if proposed.get('automation_system') != 'None' and current.get('automation_system') == 'None':
            cost += 200000  # Automation system implementation
        
        return cost
    
    def _estimate_timeline(self, proposed: Dict[str, Any]) -> int:
        """Estimate timeline for implementation in months."""
        months = 0
        
        if proposed.get('infrastructure_score', 3) > 3:
            months += 3
        
        if proposed.get('automation_system') != 'None':
            months += 2
        
        if proposed.get('barrier_score', 3) < 3:
            months += 2
        
        return max(1, months)
    
    def get_college_clusters(self) -> Dict[str, Any]:
        """
        Get college clusters using the clustering model.
        
        Returns:
            Dictionary with cluster information
        """
        if self.college_clusterer is None or not self.reference_data:
            return {'clusters': []}
        
        try:
            college_features_df = pd.DataFrame(self.reference_data.get('college_features', []))
            if college_features_df.empty:
                return {'clusters': []}
            
            # Prepare cluster features
            cluster_features = self.cluster_features if self.cluster_features else [
                'infrastructure_score', 'barrier_score', 'overall_satisfaction', 'service_efficiency'
            ]
            
            X_cluster = college_features_df[cluster_features]
            X_cluster_scaled = self.scaler.transform(X_cluster)
            clusters = self.college_clusterer.predict(X_cluster_scaled)
            
            # Get cluster labels
            cluster_labels = self.models.get('metadata', {}).get('cluster_labels', {})
            
            # Build result
            result = []
            for idx, row in college_features_df.iterrows():
                cluster_id = int(clusters[idx])
                cluster_label = cluster_labels.get(cluster_id, f'Cluster {cluster_id}')
                
                result.append({
                    'college_name': row.get('college', 'Unknown'),
                    'cluster_id': cluster_id,
                    'cluster_label': cluster_label,
                    'infrastructure_score': float(row.get('infrastructure_score', 0)),
                    'overall_satisfaction': float(row.get('overall_satisfaction', 0)),
                    'service_efficiency': float(row.get('service_efficiency', 0))
                })
            
            return {'clusters': result}
        except Exception as e:
            print(f"Error getting clusters: {e}")
            import traceback
            traceback.print_exc()
            return {'clusters': []}


    def _generate_enhanced_suggestions(self, features: Dict[str, Any], predicted_score: float) -> List[str]:
        """Generate enhanced suggestions based on features and predicted score."""
        suggestions = []
        
        # Infrastructure suggestions
        infrastructure_score = features.get('infrastructure_score', 3)
        if infrastructure_score < 3:
            suggestions.append("Upgrade hardware infrastructure and network connectivity")
        
        # Automation suggestions
        automation = features.get('automation_system', 'None')
        if automation == 'None':
            suggestions.append("Implement a library management system (KOHA or SOUL) for better efficiency")
        
        # Training suggestions
        training = features.get('ict_training_received', False)
        if not training:
            suggestions.append("Provide regular ICT training sessions for staff and users")
        
        # Performance-based suggestions
        if predicted_score < 5:
            suggestions.append("Focus on fundamental infrastructure improvements")
            suggestions.append("Establish clear ICT policies and procedures")
        elif predicted_score < 7:
            suggestions.append("Enhance digital services and user support")
            suggestions.append("Implement feedback systems for continuous improvement")
        else:
            suggestions.append("Continue current practices and explore advanced technologies")
            suggestions.append("Share best practices with other institutions")
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def get_ai_recommendations(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get AI-powered recommendations using the trained recommendation engine."""
        if not self.recommendation_classifier or not self.recommendation_templates:
            # Fallback recommendations
            return [
                {
                    'area': 'Infrastructure',
                    'action': 'Upgrade hardware and software systems',
                    'priority': 7,
                    'expectedImpact': 2.0,
                    'estimatedCost': 200000,
                    'timeline': '3-6 months'
                },
                {
                    'area': 'Training',
                    'action': 'Conduct ICT training programs',
                    'priority': 6,
                    'expectedImpact': 1.5,
                    'estimatedCost': 50000,
                    'timeline': '1-3 months'
                }
            ]
        
        try:
            # Prepare features for recommendation model
            X = self._prepare_features_recommendations(features)
            
            # Get recommendation categories
            rec_probabilities = self.recommendation_classifier.predict_proba(X)[0]
            rec_classes = self.recommendation_classifier.classes_
            
            # Get priority scores
            priority_features = [
                features.get('infrastructure_score', 3),
                features.get('barrier_score', 3),
                features.get('overall_satisfaction', 5)
            ]
            priority_X = np.array(priority_features).reshape(1, -1)
            base_priority = self.priority_model.predict(priority_X)[0] if self.priority_model else 5
            
            # Generate recommendations
            recommendations = []
            
            # Get top recommendation categories
            top_indices = np.argsort(rec_probabilities)[-3:][::-1]  # Top 3
            
            for idx in top_indices:
                if rec_probabilities[idx] > 0.1:  # Minimum confidence threshold
                    rec_type = self.recommendation_label_encoder.inverse_transform([rec_classes[idx]])[0]
                    
                    if rec_type in self.recommendation_templates:
                        for template in self.recommendation_templates[rec_type]:
                            # Adjust priority based on current state
                            adjusted_priority = min(10, max(1, 
                                template['priority'] + (base_priority - 5) * 0.5
                            ))
                            
                            recommendations.append({
                                'area': template['area'],
                                'action': template['action'],
                                'priority': round(adjusted_priority, 1),
                                'expectedImpact': template['expected_impact'],
                                'estimatedCost': template['estimated_cost'],
                                'timeline': template['timeline']
                            })
            
            # Sort by priority and return top recommendations
            recommendations.sort(key=lambda x: x['priority'], reverse=True)
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            import traceback
            traceback.print_exc()
            
            # Return fallback recommendations
            return [
                {
                    'area': 'Infrastructure',
                    'action': 'Upgrade hardware and software systems',
                    'priority': 7,
                    'expectedImpact': 2.0,
                    'estimatedCost': 200000,
                    'timeline': '3-6 months'
                }
            ]
    
    def _prepare_features_recommendations(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for recommendation model."""
        if not self.recommendation_features:
            # Fallback features
            return np.array([[
                features.get('infrastructure_score', 3),
                features.get('barrier_score', 3),
                features.get('overall_satisfaction', 5),
                features.get('awareness_level', 5),
                0, 0, 0, 0, 0  # Encoded features
            ]])
        
        feature_values = []
        for feature_name in self.recommendation_features:
            if feature_name == 'infrastructure_score':
                feature_values.append(features.get('infrastructure_score', 3))
            elif feature_name == 'barrier_score':
                feature_values.append(features.get('barrier_score', 3))
            elif feature_name == 'overall_satisfaction':
                feature_values.append(features.get('overall_satisfaction', 5))
            elif feature_name == 'service_efficiency':
                feature_values.append(features.get('service_efficiency', 5))
            elif feature_name == 'awareness_level':
                feature_values.append(features.get('awareness_level', 5))
            elif feature_name == 'automation_encoded':
                automation = features.get('automation_system', 'None')
                automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                feature_values.append(automation_map.get(automation, 0))
            elif feature_name == 'college_encoded':
                college_id = features.get('college_id', '1')
                try:
                    feature_values.append(int(college_id) - 1)
                except:
                    feature_values.append(0)
            elif feature_name == 'training_encoded':
                training = features.get('ict_training_received', False)
                feature_values.append(1 if training else 0)
            elif feature_name == 'remote_encoded':
                remote = features.get('remote_access_available', False)
                feature_values.append(1 if remote else 0)
            else:
                feature_values.append(0)
        
        return np.array(feature_values).reshape(1, -1)
    
    def _prepare_features_scenario(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for scenario models."""
        if not self.scenario_features:
            # Fallback features
            return np.array([[
                features.get('infrastructure_score', 3),
                features.get('barrier_score', 3),
                0, 0, 0, 0  # Encoded features
            ]])
        
        feature_values = []
        for feature_name in self.scenario_features:
            if feature_name == 'infrastructure_score':
                feature_values.append(features.get('infrastructure_score', 3))
            elif feature_name == 'barrier_score':
                feature_values.append(features.get('barrier_score', 3))
            elif feature_name == 'awareness_level':
                feature_values.append(features.get('awareness_level', 5))
            elif feature_name == 'automation_encoded':
                automation = features.get('automation_system', 'None')
                automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                feature_values.append(automation_map.get(automation, 0))
            elif feature_name == 'college_encoded':
                college_id = features.get('college_id', '1')
                try:
                    feature_values.append(int(college_id) - 1)
                except:
                    feature_values.append(0)
            elif feature_name == 'training_encoded':
                training = features.get('ict_training_received', False)
                feature_values.append(1 if training else 0)
            else:
                feature_values.append(0)
        
        return np.array(feature_values).reshape(1, -1)
    
    def _estimate_enhanced_cost(self, current: Dict[str, Any], proposed: Dict[str, Any]) -> float:
        """Enhanced cost estimation using scenario cost estimates."""
        if not self.scenario_cost_estimates:
            return self._estimate_cost(current, proposed)
        
        total_cost = 0
        
        # Infrastructure improvements
        infra_diff = proposed.get('infrastructure_score', 3) - current.get('infrastructure_score', 3)
        if infra_diff > 0:
            total_cost += self.scenario_cost_estimates.get('hardware_upgrade', 200000) * infra_diff / 2
        
        # Automation system upgrade
        current_auto = current.get('automation_system', 'None')
        proposed_auto = proposed.get('automation_system', 'None')
        if current_auto == 'None' and proposed_auto != 'None':
            total_cost += self.scenario_cost_estimates.get('automation_system', 300000)
        
        # Training programs
        current_training = current.get('ict_training_received', False)
        proposed_training = proposed.get('ict_training_received', False)
        if not current_training and proposed_training:
            total_cost += self.scenario_cost_estimates.get('training_program', 75000)
        
        # Internet upgrade
        internet_diff = proposed.get('internet_speed', 3) - current.get('internet_speed', 3)
        if internet_diff > 0:
            total_cost += self.scenario_cost_estimates.get('internet_upgrade', 50000) * internet_diff / 2
        
        return max(25000, total_cost)  # Minimum cost
    
    def _calculate_enhanced_roi(self, improvement: float, cost: float) -> float:
        """Calculate enhanced ROI considering long-term benefits."""
        if cost <= 0:
            return 0
        
        # Estimate annual benefits (in monetary terms)
        # Assume each improvement point translates to efficiency gains
        annual_benefit = improvement * 50000  # ₹50k per improvement point per year
        
        # Calculate ROI over 5 years
        total_benefit = annual_benefit * 5
        roi = total_benefit / cost
        
        return max(0, roi)
    
    def _estimate_enhanced_timeline(self, current: Dict[str, Any], proposed: Dict[str, Any]) -> int:
        """Enhanced timeline estimation based on complexity of changes."""
        timeline_months = 1  # Base timeline
        
        # Infrastructure changes
        infra_diff = proposed.get('infrastructure_score', 3) - current.get('infrastructure_score', 3)
        if infra_diff > 1:
            timeline_months += 3  # Major infrastructure changes
        elif infra_diff > 0:
            timeline_months += 1  # Minor infrastructure changes
        
        # Automation system implementation
        current_auto = current.get('automation_system', 'None')
        proposed_auto = proposed.get('automation_system', 'None')
        if current_auto == 'None' and proposed_auto != 'None':
            timeline_months += 2  # Automation implementation
        
        # Training programs
        current_training = current.get('ict_training_received', False)
        proposed_training = proposed.get('ict_training_received', False)
        if not current_training and proposed_training:
            timeline_months += 1  # Training programs
        
        return min(12, timeline_months)  # Maximum 12 months

    def _prepare_features_enhanced_efficiency(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for enhanced efficiency models."""
        if not self.enhanced_efficiency_features:
            # Fallback features
            return np.array([[
                features.get('infrastructure_score', 3),
                features.get('barrier_score', 3),
                features.get('awareness_level', 5),
                0, 0, 0, 0  # Encoded features
            ]])
        
        feature_values = []
        for feature_name in self.enhanced_efficiency_features:
            if feature_name == 'infrastructure_score':
                feature_values.append(features.get('infrastructure_score', 3))
            elif feature_name == 'barrier_score':
                feature_values.append(features.get('barrier_score', 3))
            elif feature_name == 'awareness_level':
                feature_values.append(features.get('awareness_level', 5))
            elif feature_name == 'automation_encoded':
                automation = features.get('automation_system', 'None')
                automation_map = {'None': 0, 'KOHA': 1, 'SOUL': 2, 'Other': 3}
                feature_values.append(automation_map.get(automation, 0))
            elif feature_name == 'college_encoded':
                college_id = features.get('college_id', '1')
                try:
                    feature_values.append(int(college_id) - 1)
                except:
                    feature_values.append(0)
            elif feature_name == 'training_encoded':
                training = features.get('ict_training_received', False)
                feature_values.append(1 if training else 0)
            elif feature_name == 'remote_encoded':
                remote = features.get('remote_access_available', False)
                feature_values.append(1 if remote else 0)
            else:
                feature_values.append(0)
        
        return np.array(feature_values).reshape(1, -1)


# Global ML service instance
ml_service = MLService()
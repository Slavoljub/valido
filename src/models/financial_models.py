"""
Financial Analysis Models
Integration of existing financial analysis functionality from src/models
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

from ..core_config.config import Configuration
from .ai_models import OpenAIWrapper, BaseAIService

logger = logging.getLogger(__name__)


class FinancialAnalyzer(BaseAIService):
    """Financial analysis service using existing models"""
    
    def __init__(self, openai_wrapper: OpenAIWrapper):
        super().__init__(openai_wrapper)
        config = Configuration()
        self.data_path = Path(config.paths.data_folder)
    
    def process_request(self, user_message: str, **kwargs) -> Dict[str, Any]:
        """Process financial analysis request"""
        try:
            # Import existing functions
            from src.models.ai_finansije import (
                generisi_ai_svesku_sa_trendom,
                ucitaj_dobavljace_putanja,
                ucitaj_plate_putanja
            )
            
            # Process based on request type
            if "sveska" in user_message.lower() or "trend" in user_message.lower():
                return self._analyze_financial_trends(**kwargs)
            elif "dobavljaci" in user_message.lower():
                return self._analyze_suppliers(**kwargs)
            elif "plate" in user_message.lower() or "zarade" in user_message.lower():
                return self._analyze_salaries(**kwargs)
            else:
                return self._general_financial_analysis(user_message, **kwargs)
                
        except Exception as e:
            logger.error(f"Financial analysis failed: {e}")
            return {
                'response': f"Greška pri finansijskoj analizi: {str(e)}",
                'status': 'error'
            }
    
    def _analyze_financial_trends(self, **kwargs) -> Dict[str, Any]:
        """Analyze financial trends using existing model"""
        try:
            # Load data files
            dobavljaci_path = self.data_path / "mom21" / "specifikacija_dobavljaca" / "specifikacija_dobavljaca_ai.csv"
            plate_path = self.data_path / "mom21" / "plate" / "plate_2024.csv"
            
            if not dobavljaci_path.exists() or not plate_path.exists():
                return {
                    'response': "Podaci za analizu nisu dostupni. Proverite putanje do fajlova.",
                    'status': 'error'
                }
            
            # Load data
            df_dobavljaci = pd.read_csv(dobavljaci_path)
            df_plate = pd.read_csv(plate_path)
            
            # Use existing analysis function
            from src.models.ai_finansije import generisi_ai_svesku_sa_trendom
            
            result = generisi_ai_svesku_sa_trendom(df_dobavljaci, df_plate, "2024")
            
            return {
                'response': result.get('gpt_tekst', 'Analiza završena'),
                'data': result,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {
                'response': f"Greška pri analizi trenda: {str(e)}",
                'status': 'error'
            }
    
    def _analyze_suppliers(self, **kwargs) -> Dict[str, Any]:
        """Analyze supplier data"""
        try:
            from src.models.ai_finansije import ucitaj_dobavljace_putanja
            
            dobavljaci_path = self.data_path / "mom21" / "specifikacija_dobavljaca" / "specifikacija_dobavljaca_ai.csv"
            
            if not dobavljaci_path.exists():
                return {
                    'response': "Fajl sa podacima o dobavljačima nije dostupan.",
                    'status': 'error'
                }
            
            df_dobavljaci = ucitaj_dobavljace_putanja(str(dobavljaci_path))
            
            # Basic analysis
            total_suppliers = len(df_dobavljaci)
            total_amount = df_dobavljaci['promet'].sum()
            avg_amount = df_dobavljaci['promet'].mean()
            
            analysis = f"""
Analiza dobavljača:
- Ukupno dobavljača: {total_suppliers}
- Ukupan promet: {total_amount:,.2f} RSD
- Prosečan promet po dobavljaču: {avg_amount:,.2f} RSD
- Najveći dobavljač: {df_dobavljaci.loc[df_dobavljaci['promet'].idxmax(), 'dobavljac']}
- Najmanji dobavljač: {df_dobavljaci.loc[df_dobavljaci['promet'].idxmin(), 'dobavljac']}
            """
            
            return {
                'response': analysis,
                'data': {
                    'total_suppliers': total_suppliers,
                    'total_amount': total_amount,
                    'avg_amount': avg_amount,
                    'suppliers_data': df_dobavljaci.to_dict('records')
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Supplier analysis failed: {e}")
            return {
                'response': f"Greška pri analizi dobavljača: {str(e)}",
                'status': 'error'
            }
    
    def _analyze_salaries(self, **kwargs) -> Dict[str, Any]:
        """Analyze salary data"""
        try:
            from src.models.ai_finansije import ucitaj_plate_putanja
            
            plate_path = self.data_path / "mom21" / "plate" / "plate_2024.csv"
            
            if not plate_path.exists():
                return {
                    'response': "Fajl sa podacima o platama nije dostupan.",
                    'status': 'error'
                }
            
            df_plate = ucitaj_plate_putanja(str(plate_path))
            
            # Basic analysis
            total_employees = len(df_plate)
            total_salary = df_plate['Bruto 2'].sum()
            avg_salary = df_plate['Bruto 2'].mean()
            
            analysis = f"""
Analiza plata:
- Ukupno zaposlenih: {total_employees}
- Ukupno isplaćeno: {total_salary:,.2f} RSD
- Prosečna plata: {avg_salary:,.2f} RSD
- Najviša plata: {df_plate['Bruto 2'].max():,.2f} RSD
- Najniža plata: {df_plate['Bruto 2'].min():,.2f} RSD
            """
            
            return {
                'response': analysis,
                'data': {
                    'total_employees': total_employees,
                    'total_salary': total_salary,
                    'avg_salary': avg_salary,
                    'salary_data': df_plate.to_dict('records')
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Salary analysis failed: {e}")
            return {
                'response': f"Greška pri analizi plata: {str(e)}",
                'status': 'error'
            }
    
    def _general_financial_analysis(self, user_message: str, **kwargs) -> Dict[str, Any]:
        """General financial analysis using AI"""
        try:
            messages = [
                {"role": "system", "content": "Ti si finansijski analitičar koji pomaže sa analizom podataka."},
                {"role": "user", "content": user_message}
            ]
            
            response = self.openai.chat_completion(messages)
            
            if response and response.get('status') == 'success':
                return {
                    'response': response.get('response'),
                    'status': 'success'
                }
            else:
                return {
                    'response': 'Greška pri AI analizi',
                    'status': 'error'
                }
                
        except Exception as e:
            logger.error(f"General analysis failed: {e}")
            return {
                'response': f"Greška pri analizi: {str(e)}",
                'status': 'error'
            }


class SalaryAnalyzer(BaseAIService):
    """Salary analysis service using existing models"""
    
    def __init__(self, openai_wrapper: OpenAIWrapper):
        super().__init__(openai_wrapper)
        config = Configuration()
        self.data_path = Path(config.paths.data_folder)
    
    def process_request(self, user_message: str, **kwargs) -> Dict[str, Any]:
        """Process salary analysis request"""
        try:
            # Import existing salary analysis functions
            from src.models.get_salary_details import get_salary_details, analyze_salary_trends
            
            # Process based on request type
            if "detalji" in user_message.lower():
                return self._get_salary_details(**kwargs)
            elif "anomalija" in user_message.lower():
                return self._detect_salary_anomalies(**kwargs)
            else:
                return self._general_salary_analysis(user_message, **kwargs)
                
        except Exception as e:
            logger.error(f"Salary analysis failed: {e}")
            return {
                'response': f"Greška pri analizi plata: {str(e)}",
                'status': 'error'
            }
    
    def _get_salary_details(self, **kwargs) -> Dict[str, Any]:
        """Get detailed salary information"""
        try:
            # Implementation would use existing salary analysis functions
            return {
                'response': 'Detaljna analiza plata je u pripremi.',
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Salary details failed: {e}")
            return {
                'response': f"Greška pri dobavljanju detalja o platama: {str(e)}",
                'status': 'error'
            }
    
    def _detect_salary_anomalies(self, **kwargs) -> Dict[str, Any]:
        """Detect salary anomalies"""
        try:
            # Implementation would use existing anomaly detection
            return {
                'response': 'Detekcija anomalija u platama je u pripremi.',
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {
                'response': f"Greška pri detekciji anomalija: {str(e)}",
                'status': 'error'
            }
    
    def _general_salary_analysis(self, user_message: str, **kwargs) -> Dict[str, Any]:
        """General salary analysis using AI"""
        try:
            messages = [
                {"role": "system", "content": "Ti si analitičar plata koji pomaže sa analizom podataka o zaradama."},
                {"role": "user", "content": user_message}
            ]
            
            response = self.openai.chat_completion(messages)
            
            if response and response.get('status') == 'success':
                return {
                    'response': response.get('response'),
                    'status': 'success'
                }
            else:
                return {
                    'response': 'Greška pri AI analizi plata',
                    'status': 'error'
                }
                
        except Exception as e:
            logger.error(f"General salary analysis failed: {e}")
            return {
                'response': f"Greška pri analizi plata: {str(e)}",
                'status': 'error'
            }

from typing import Dict, Optional
from database import Database

class CommissionCalculator:
    
    @staticmethod
    def calculate_commission_for_seller(property_type: str, monthly_price: float) -> float:
        if property_type == 'apartment':
            return 3000 + monthly_price
        elif property_type == 'land':
            yearly_price = monthly_price * 12
            return 5000 + (yearly_price * 0.05)
        elif property_type == 'house':
            return 5000 + (monthly_price * 0.25)
        else:
            return 0.0
    
    @staticmethod
    def calculate_commission_for_buyer(monthly_price: float) -> float:
        return monthly_price * 0.10
    
    @staticmethod
    def calculate_deal_commissions(deal: Dict, db: Database) -> Dict[str, float]:
        if not deal or 'offer' not in deal:
            return {
                'seller_commission': 0.0,
                'buyer_commission': 0.0,
                'seller_realtor_share': 0.0,
                'buyer_realtor_share': 0.0,
                'company_share': 0.0
            }
        
        offer = deal['offer']
        property_data = offer.get('property', {})
        property_type = property_data.get('type', 'apartment')
        monthly_price = float(offer.get('price', 0))
        
        seller_commission = CommissionCalculator.calculate_commission_for_seller(property_type, monthly_price)
        buyer_commission = CommissionCalculator.calculate_commission_for_buyer(monthly_price)
        
        seller_realtor_id = offer.get('realtor_id')
        buyer_realtor_id = deal.get('demand', {}).get('realtor_id')
        
        seller_realtor = db.get_realtor(seller_realtor_id) if seller_realtor_id else None
        buyer_realtor = db.get_realtor(buyer_realtor_id) if buyer_realtor_id else None
        
        seller_share = (seller_realtor.get('commission_share') or 45.0) / 100.0 if seller_realtor else 0.45
        buyer_share = (buyer_realtor.get('commission_share') or 45.0) / 100.0 if buyer_realtor else 0.45
        
        seller_realtor_share = seller_commission * seller_share
        buyer_realtor_share = buyer_commission * buyer_share
        
        company_share = (seller_commission - seller_realtor_share) + (buyer_commission - buyer_realtor_share)
        
        return {
            'seller_commission': round(seller_commission, 2),
            'buyer_commission': round(buyer_commission, 2),
            'seller_realtor_share': round(seller_realtor_share, 2),
            'buyer_realtor_share': round(buyer_realtor_share, 2),
            'company_share': round(company_share, 2)
        }


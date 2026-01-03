import pandas as pd
from django.core.management.base import BaseCommand
from recharge.models import Plan, Operator

class Command(BaseCommand):
    help = 'Import recharge plans from excel file'

    def handle(self, *args, **kwargs):
        file_path = 'recharge_plans.xlsx'
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading excel file: {e}'))
            return

        self.stdout.write(f"Found columns: {list(df.columns)}")
        
        # Normalize columns
        df.columns = [c.strip() for c in df.columns]
        
        all_ops = list(Operator.objects.values_list('name', flat=True))
        self.stdout.write(f"Existing Operators in DB: {all_ops}")
        
        def get_col(row, candidates):
            for c in candidates:
                if c in row:
                    return row[c]
            return None

        count = 0
        for index, row in df.iterrows():
            operator_name = str(get_col(row, ['OPERATOR', 'Operator']) or '').strip()
            if not operator_name or operator_name.lower() == 'nan':
                continue
                
            try:
                # Case insensitive match for operator
                operator = Operator.objects.get(name__iexact=operator_name)
            except Operator.DoesNotExist:
                # self.stdout.write(self.style.WARNING(f"  FAILED: Operator '{operator_name}' not found in DB."))
                continue
            except Operator.MultipleObjectsReturned:
                operator = Operator.objects.filter(name__iexact=operator_name).first()
                # self.stdout.write(self.style.WARNING(f"  WARNING: Multiple operators found for '{operator_name}'. Using first one."))

            amount = get_col(row, ['AMOUNT', 'Amount', 'amount'])
            if not amount or pd.isna(amount):
                continue
                
            plan_type_raw = str(get_col(row, ['PLAN TYPE', 'Plan Type', 'Plan_Type']) or '').strip()
            
            # Map known types
            type_map = {
                'UNLIMITED': 'UNLIMITED',
                'DATA': 'DATA',
                'TALKTIME': 'TOPUP',
                'TOPUP': 'TOPUP',
                'SMS': 'SMS',
                'ROAMING': 'ROAMING',
                'VAS': 'OTHER',
                'VALIDITY EXTENSION': 'OTHER',
                'IST': 'OTHER',
            }
            
            plan_type_upper = plan_type_raw.upper()
            plan_type = type_map.get(plan_type_upper, 'OTHER')
            
            # If not mapped and length > 20, truncate or default to OTHER
            if len(plan_type) > 20:
                self.stdout.write(self.style.WARNING(f"  WARNING: Plan Type '{plan_type_raw}' too long. Defaulting to OTHER."))
                plan_type = 'OTHER'

            validity = get_col(row, ['Validity', 'VALIDITY']) or ''
            data = get_col(row, ['Data', 'DATA']) or ''
            benefits = get_col(row, ['Additional Benefits', 'Aditional Benefits', 'ADDITIONAL BENEFITS']) or ''
            circle = get_col(row, ['Circle', 'CIRCLE']) or 'ALL'

            try:
                Plan.objects.create(
                    operator=operator,
                    amount=amount,
                    validity=validity,
                    data=data,
                    additional_benefits=benefits,
                    plan_type=plan_type,
                    circle=circle
                )
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ERROR creating plan: {e}"))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} plans.'))

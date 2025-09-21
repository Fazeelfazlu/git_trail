import pyotp
from create_app import app,config_data
class OTPManager:

    @staticmethod
    def get_setup_uri(username,token):
        return pyotp.totp.TOTP(token).provisioning_uri(
            name=username, issuer_name=config_data["APP_NAME"])
    

    @staticmethod
    def validate_otp(otp,username,token):
        otpobj = pyotp.parse_uri(OTPManager.get_setup_uri(username,token))
        return otpobj.verify(otp)
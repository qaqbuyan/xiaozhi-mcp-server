import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger('标准体重计算器')

def get_standard_weight_calculator(mcp: FastMCP):
    """标准体重"""
    @mcp.tool()
    def get_standard_weight_calculator(sex: str, height: str, weight: str) -> dict:
        """标准体重（BMI）计算器，通过身高和体重来计算您的身材是否是美少年或者美少女。
        需要告诉用户不适合BMI评判人群：
            1、未满18岁；
            2、运动员；
            3、正在做重量训练；
            4、怀孕或哺乳中；
            5、身体虚弱或久坐不动的老人。
        Args:
            sex (str): 性别，必填，只能是男、女、male 或 female
            height (str): 身高，必填，单位为厘米
            weight (str): 体重，必填，单位为千克
        Returns:
            dict: 包含操作结果的字典，格式为 {
                "success": bool,  # 是否成功
                "result": str  # 计算结果描述
            }
        """
        try:
            logger.info('开始计算标准体重...')
            logger.info(f'性别: {sex}, 身高: {height}, 体重: {weight}')
            try:
                height_num = float(height)
                weight_num = float(weight)
            except ValueError:
                return {"success": False, "result": "身高和体重必须为有效数字"}
            sex = sex.lower()
            if sex not in ['男', '女', 'male', 'female']:
                return {"success": False, "result": "性别参数只能是男、女、male 或 female"}
            if sex in ['男', 'male']:
                standard_weight = (height_num - 80) * 0.7
                category = '美少年'
            else:
                standard_weight = (height_num - 70) * 0.6
                category = '美少女'
            weight_diff = ((weight_num - standard_weight) / standard_weight) * 100
            height_m = height_num / 100
            bmi = weight_num / (height_m ** 2)
            norm_bmi_min = 18.5
            norm_bmi_max = 23.9
            ideal_weight_min = norm_bmi_min * (height_m ** 2)
            ideal_weight_max = norm_bmi_max * (height_m ** 2)
            if -10 <= weight_diff <= 10:
                result = f"您是{category}身材，体重正常。当前体重 {weight_num}kg，标准体重 {standard_weight:.2f}kg。" 
            elif weight_diff < -10:
                result = f"您低于{category}标准体重，偏瘦。当前体重 {weight_num}kg，标准体重 {standard_weight:.2f}kg。" 
            else:
                result = f"您高于{category}标准体重，偏胖。当前体重 {weight_num}kg，标准体重 {standard_weight:.2f}kg。" 
            if bmi <= 18.4:
                bmi_status = "体质偏瘦"
            elif 18.5 <= bmi <= 23.9:
                bmi_status = "体质正常"
            elif 24.0 <= bmi <= 27.9:
                bmi_status = "体质过重"
            elif 28.0 <= bmi <= 32.0:
                bmi_status = "体质肥胖"
            else:
                bmi_status = "重度肥胖"
            result += f"体重偏差百分比: {weight_diff:.2f}%，BMI: {bmi:.2f}，{bmi_status}，正常 BMI 范围: {norm_bmi_min:.1f}-{norm_bmi_max:.1f}，理想体重范围: {ideal_weight_min:.2f}-{ideal_weight_max:.2f}kg。" 
            logger.info('标准体重计算完成')
            logger.info(f'标准体重计算结果: {result}')
            return {"success": True, "result": result}
        except Exception as e:
            error_msg = f"计算标准体重失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "result": error_msg}
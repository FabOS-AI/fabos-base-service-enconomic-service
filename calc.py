from wbd_calculation.WBDCalc_withAAS import CostsMaschineBase
from wbd_calculation.WBDCalc_withAAS import CostsAI

costsBase = CostsMaschineBase()
costsAI = CostsAI()

costsBase.init_submodel()
costsBase.calc()
costsAI.calc()
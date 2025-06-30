BT-LAB SETTING FILE

Number of linked techniques : 1

BT-LAB for windows v1.73 (software)
Internet server v1.73 (firmware)
Command interpretor v1.73 (firmware)

Filename : ncm909-pr-465

Device : BCS-810
Ecell ctrl range : min = 0.00 V, max = 10.00 V
Electrode material : ncm909-pr-465
Initial state : 
Electrolyte : 
Comments : 
Mass of active material : 0.001 mg
 at x = 0.000
Molecular weight of active material (at x = 0) : 0.001 g/mol
Atomic weight of intercalated ion : 0.001 g/mol
Acquisition started at : xo = 0.000
Number of e- transfered per intercalated ion : 1
for DX = 1, DQ = 26.802 mA.h
Battery capacity : 2500 mA.h
Electrode surface area : 0.001 cm²
Characteristic mass : 10 g
Volume (V) : 0.001 cm³
Cycle Definition : Charge/Discharge alternance
Turn to OCV between techniques

Technique : 1
Modulo Bat
Ns                  0                   1                   2                   3                   4                   5                   
ctrl_type           Rest                CC-CV               Rest                PEIS                Rest                CC                  
Apply I/C           I                   C / N               C / N               C / N               C / N               C / N               
current/potential   current             current             current             current             current             current             
ctrl1_val                               0.000                                   10.000                                  5.000               
ctrl1_val_unit                          mA                                      mV                                      mA                  
ctrl1_val_vs                                                                                                            <None>              
ctrl2_val                               4.300                                   10.000                                                      
ctrl2_val_unit                          V                                       kHz                                                         
ctrl2_val_vs                                                                                                                                
ctrl3_val                               0.050                                   0.100                                                       
ctrl3_val_unit                          mA                                      Hz                                                          
ctrl3_val_vs                                                                                                                                
N                   1.00                10.00               10.00               10.00               10.00               10.00               
charge/discharge    Charge              Charge              Charge              Charge              Charge              Discharge           
charge/discharge_1  Charge              Charge              Charge              Charge              Charge              Charge              
Apply I/C_1         I                   I                   I                   I                   I                   I                   
N1                  0.00                1.00                1.00                1.00                1.00                1.00                
ctrl4_val                               0.000                                                                                               
ctrl4_val_unit                          mA/s                                                                                                
ctrl5_val                               0.000                                                                                               
ctrl5_val_unit                          mn                                                                                                  
ctrl_tM             0                   0                   0                   0                   0                   0                   
ctrl_seq            0                   0                   0                   0                   0                   0                   
ctrl_repeat         0                   0                   0                   0                   0                   0                   
ctrl_trigger        Falling Edge        Falling Edge        Falling Edge        Falling Edge        Falling Edge        Falling Edge        
ctrl_TO_t           0.000               0.000               0.000               0.000               0.000               0.000               
ctrl_TO_t_unit      d                   d                   d                   d                   d                   d                   
ctrl_Nd             6                   6                   6                   6                   6                   6                   
ctrl_Na             1                   1                   1                   1                   1                   1                   
ctrl_corr           0                   0                   0                   0                   0                   0                   
lim_nb              1                   1                   1                   0                   1                   2                   
lim1_type           Time                Time                Time                Time                Time                Ecell               
lim1_comp           >                   >                   >                   >                   >                   <                   
lim1_Q              Q limit             Q limit             Q limit             Q limit             Q limit             Q limit             
lim1_value          360.000             10.000              10.000              10.000              10.000              2.500               
lim1_value_unit     mn                  h                   mn                  h                   mn                  V                   
lim1_action         Next sequence       Next sequence       Next sequence       Next sequence       Next sequence       Next sequence       
lim1_seq            1                   2                   3                   4                   5                   6                   
lim2_type           Time                Time                Time                Time                Time                Time                
lim2_comp           <                   <                   <                   <                   <                   >                   
lim2_Q              Q limit             Q limit             Q limit             Q limit             Q limit             Q limit             
lim2_value          0.000               0.000               0.000               0.000               0.000               10.000              
lim2_value_unit     s                   s                   s                   s                   s                   h                   
lim2_action         Next sequence       Next sequence       Next sequence       Next sequence       Next sequence       Next sequence       
lim2_seq            1                   2                   3                   4                   5                   6                   
rec_nb              1                   1                   1                   0                   1                   1                   
rec1_type           Time                Time                Time                Time                Time                Time                
rec1_value          60.000              60.000              60.000              60.000              60.000              60.000              
rec1_value_unit     s                   s                   s                   s                   s                   s                   
E range min (V)     0.000               0.000               0.000               0.000               0.000               0.000               
E range max (V)     10.000              10.000              10.000              10.000              10.000              10.000              
I Range             10 mA               1 mA                1 mA                1 mA                1 mA                1 mA                
I Range min         Unset               Unset               Unset               Unset               Unset               Unset               
I Range max         Unset               Unset               Unset               Unset               Unset               Unset               
I Range init        Unset               Unset               Unset               Unset               Unset               Unset               
auto rest           0                   0                   0                   0                   0                   0                   
Bandwidth           4                   4                   4                   4                   4                   4                   

# Master Asset Register Repair Instructions

The corrected Build 0038 import must update `Documentation/Master_Asset_Register.csv`.

After successful import, select **Open Master Asset Register** in Project Genesis. The file must contain populated permanent identifiers and must not contain `NO NEW UAI`.

If the installed Project Genesis interface reports that post-apply hooks are unsupported, run `13_Project_Genesis/Import/Run_Master_Asset_Register_Repair.cmd` once, then reopen the register.

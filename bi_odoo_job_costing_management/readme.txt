Date 16th march 2020
version 13.0.0.1
	- -->Job order and job cost sheet should be linked and once job order has been selected the planning material should be fetched in the job cost sheet .
	-->vendors field should be required field for the purchase order not for the internal picking in “material requisition”
	-->job type field should be added in job order
	-->job cost sheet-->material tab-->material should be selected automatically and should be read only
	-->job cost sheet-->overhead tab-->overhead should be selected automatically and should be read only
	-->job cost sheet-->labour tab-->labour should be selected automatically and should be read only
	-->purchase requisition-->received date field should be non editable .

Date 17th march 2020
version 13.0.0.2
	- actual quantity and invoice quantity generate error while multiple job cost sheet added.

Date 18th march 2020
version 13.0.0.3
	- cost sheet should be selected automatically in purchase order and vendor bill (if in the purchase requisition cost sheet is selected )
	- Total Cost =Total cost (Cost sheet 1)+Total cost (Cost sheet 2)+...Total cost (Cost sheet n)
	- Total Cost of Project should be display in the project
	- Cost unit should be fetched from the product template
	- In Labour tab only service product should be selected
	- job order select job type is labour its filter with serviceable product

Date 25th march 2020
version 13.0.0.4
improvement:-
	- project issue solve
	- job note issue solve
	- requisition line added new , remove all lines , and added new line when job order changes.
	- unit price update with lst price.
	- some fields readony according to stage changes.
	- moves and purchase order not link with purchase requisition solve.


version 13.0.0.5
improvement:-
	- Job cost sheet the product are fetched multiple time  when we click the job order
	-->In Purchase order "Job order" name should be changed to "job cost sheet" and the cost sheet name should be fetched from the purchase requisition .. 
	-->In Internal Picking and incoming shipment  form view  change the name of the "Job Material requisition"to job order
	---> Actual Purchase and Actual Invoice quantity not get properly
	-->  actual requisition qty update when material requisition generate
	---> cost/unit price update product cost price now

version 13.0.0.6
improvement:- 
	- Actual invoice quantity will be only calculated based on customer invoice.
	- All the actual quantities will be updated when PO or invoice is not in draft state.	

13.0.0.7 ==> removed task_id field and uncommented code of customer rating.

13.0.0.8 ==> Job cost sheet the analytic account will be fetched from the project analytic account. 

13.0.0.9 ==>solved issues of Days to assign ,Days to close ,working Hours to assign issue,working hours to close issue ,days since last action ,Date since creation.

13.0.1.0 --> Description displayed in material, labour and overhead.
		 -->  Hours value updated in labour tab
		 -->  All the tabs in job cost sheet are readonly.  
		 -->  Initially planned hours field is in 00:00 format.
13.0.1.1 ==>added condition for date_create.

13.0.1.2 ==> changed field in stock.picking
13.0.1.3 ==>added validation for date.

13.0.1.4
	Improvements:
	-Added actual requisition quantity and also smart button displaying number of requisitions linked to current job cost sheet. 
    - Fixed the issue of invoice quantity not getting updated. 
    - Fixed job order report view. In material requisition tab,the fields which are displayed in job order form view will be displayed in reports. 
    - Fixed the issue of not displaying multiple usernames in timesheet tab of Job order report. 
    - Resolved the issue of purchase order count, invoice count not getting updated in job cost sheet.

13.0.1.5
	Improvement:
		- Removed the actual requisition quantity flow as it is already present in bi_material_requisition_cost_sheet module.     

version 13.0.1.6
	- Fix the issue when duplicate job cost sheet.
	- Improve _get_invoice_line_count method.

#task 1 and 2
import matplotlib.pyplot as pt
import pandas as pd

df =pd.read_csv('/company_sales_data.csv',sep = ',')
col_list=df.columns

df['total_profit']
x = df['month_number']
y = df['total_units']
pt.plot(x, y, ms = 10,marker = "o", color = 'red', mfc = 'green', mec = 'black', ls='--', linewidth=3, label=col_list[-1])
pt.xticks(x)
pt.xlabel(col_list[0])
pt.ylabel(col_list[-1])
pt.title('company profit per month')
pt.legend(loc='lower right')
pt.show()


#task 5
pt.bar(x - 0.2, df[col_list[1]], 0.4, color = 'blue')
pt.bar(x + 0.2, df[col_list[2]], 0.4, color = 'orange')

pt.xlabel(col_list[0])
pt.ylabel('sales untils in numbers')
pt.title('facewash and facecream sales data')
pt.legend()
pt.show()

#task 6
fig = pt.figure(figsize=(10, 7))
data= []
for col in col_list[1:-2]:
  g = sum(df[col])
  data.append(g)
total_d = sum(data)
percent = [(d / total_d) * 100 for d in data]



pt.pie(percent, labels=col_list[1:-2])
pt.legend(col_list[1:-2])
pt.title('sales data')
pt.show()

#task 8
ax = pt.subplots(1,1)
ax = pt.subplots(1,3)

for col in col_list[1:-2]:
  pt.plot(x, df[col], label = col,  marker = 'o', ms = 5)

pt.xlabel(col_list[0])
pt.ylabel('sales untils in numbers')
pt.title('sales data')
pt.legend()
pt.show()


fig, axs = pt.subplots(2, figsize = (15, 5))
axs[0].plot(x, df[col_list[4]], marker = 'o',  ms = 5, color = 'black')
axs[1].plot(x, df[col_list[2]], marker = 'o',  ms = 5, color = 'red')
axs[0].set(title='sales data of bathingsoap', ylabel='', xlabel= '')
axs[1].set(title='sales data of facewash', ylabel='sales untils in numbers', xlabel= 'month number')

pt.grid(linestyle = '--', linewidth = 1)
pt.scatter(x, df[col_list[3]], marker = 'o')
pt.xticks(x)
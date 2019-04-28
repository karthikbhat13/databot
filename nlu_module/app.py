from flask import Flask, request, jsonify
import info
import filter
from flask_cors import CORS
import retry

app = Flask(__name__)
CORS(app)

clear_flag = False
df = None
info = {}
pre_col = ''

@app.route('/')
def index():
   return 'index'

@app.route('/user_input', methods=['POST'])
def user_input():
   data = request.form

   inp = data['user_input']
   flag = data['sessionDone']

   global df
   global info
   global pre_col
   global clear_flag

   print(flag)
   if int(flag) == 1:
      clear_flag = True
   print(clear_flag)
   if clear_flag:
      clear_flag = False
      df, info = filter.filter(inp)
      df, col = state(df, info)

      if df.empty:
         df = retry.no_col_match(inp)
         df, col = state(df, info)
            
      if col == '':
         
         ret_rows = df[[info['cols'][0]]].values
         print(ret_rows)
         ret_rows = [row[0] for row in ret_rows]
         json = {}
         json['text'] = ', '.join(list(ret_rows))
         json['sessionDone'] = 1
         return jsonify(json)
      else:
         json = {}         
         json['text'] = str(col)
         json['sessionDone'] = 0
         pre_col = col
         return jsonify(json)

   else:
      print(pre_col)
      print(inp)
      ret_df = df[df[pre_col] == inp]
      ret_rows, col = state(ret_df, info)


      if df.empty:
         df = retry.no_col_match(inp)
         df, col = state(df, info)
         
      if col == '':
         ret_rows_final = ret_rows[[info['cols'][0]]].values
         print(ret_rows_final)
         ret_rows_final = [row[0] for row in ret_rows_final]
         json = {}
         json['text'] = ', '.join(list(ret_rows_final))
         json['sessionDone'] = 1
         return jsonify(json)
      else:
         json = {}         
         json['text'] = str(col)
         json['sessionDone'] = 0
         pre_col = col
         return jsonify(json)

      
def state(rows, intent_info):
   print(len(rows.index)) 
   if len(rows.index) > 2:
      cols = list(rows.columns.values)
      print(cols)

      for col in intent_info['cols']:
         cols.remove(col)
      max_row = 0
      fin_col = ''
      for col in cols:
         if len(rows[col].unique()) > max_row and col != 'Rank' and col!='Votes':
            fin_col = col
            max_row = len(rows[col].unique())
      print(fin_col)

      intent_info['cols'].append(fin_col)
      final_rows = rows[intent_info['cols']]
      print(final_rows)

      return rows, fin_col
   else:
      return rows, '' 
   return 'test'

if __name__ == "__main__":
    app.run(debug=True)
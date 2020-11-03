class CreateComments < ActiveRecord::Migration[6.0]
  def change
    create_table :comments do |t|
      t.references :post, index: true, foreign_key: true
      t.text :body

      t.timestamps null false
    end
  end
end

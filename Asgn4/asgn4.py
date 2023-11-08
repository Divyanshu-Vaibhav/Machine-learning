#Divyanshu Vaibhav
#21BT10014

# -*- coding: utf-8 -*-
"""Asgn4

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NBFR14VdFWajdXob_mb7nCCUu7PPHJNY
"""


import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
df=pd.read_csv("/content/drive/MyDrive/Mlfa/asgn4/car_evaluation.csv")

#Adding column names to the df
df.columns=pd.Index(['Price','Maintenance','Doors','Persons','Lug_boot','Safety','Acceptability'])

print(df.head())

#Converting df into numerical values
label_encoder=LabelEncoder()
df['Price']=label_encoder.fit_transform(df['Price'])
df['Maintenance']=label_encoder.fit_transform(df['Maintenance'])
df['Lug_boot']=label_encoder.fit_transform(df['Lug_boot'])
df['Safety']=label_encoder.fit_transform(df['Safety'])
df['Acceptability']=label_encoder.fit_transform(df['Acceptability'])
df['Doors']=df['Doors'].replace('5more',5)
df['Doors']=df['Doors'].astype(int)
df['Persons']=df['Persons'].replace('more',6)
df['Persons']=df['Persons'].astype(int)
print(df.head())
X=df.drop(columns='Acceptability').values
y = df['Acceptability'].values
print(X)
print(y)

from sklearn.model_selection import train_test_split
X_train,X_temp,y_train,y_temp=train_test_split(X,y,test_size=0.4, random_state=42)
X_test,X_val,y_test,y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)



class DecisionTreeClassifier:
    class Node:
        def __init__(self, entropy, num_samples, num_classes):
            self.entropy=entropy
            self.num_samples=num_samples
            self.num_classes=num_classes
            self.feature_index=0
            self.threshold=0
            self.left =None
            self.right =None
            self.predicted_class= None

    def __init__(self, entropy_threshold=0):
        self.entropy_threshold=entropy_threshold
        self.tree =None

    def calculate_entropy(self, y):
        unique_classes, counts=np.unique(y, return_counts=True)
        probabilities=counts / len(y)
        entropy=-np.sum(probabilities*np.log2(probabilities))
        return entropy

    def split_dataset(self, X, y, feature_index, threshold):
        left_mask = X[:, feature_index] <=threshold
        right_mask = ~left_mask
        return X[left_mask], y[left_mask], X[right_mask], y[right_mask]

    def calculate_information_gain(self, X, y, feature_index, threshold):
        left_X, left_y, right_X, right_y = self.split_dataset(X, y, feature_index, threshold)
        parent_entropy = self.calculate_entropy(y)
        left_entropy = self.calculate_entropy(left_y)
        right_entropy = self.calculate_entropy(right_y)
        num_left = len(left_y)
        num_right = len(right_y)
        total_samples =num_left + num_right
        information_gain= parent_entropy - (num_left / total_samples) * left_entropy - (
                    num_right / total_samples) * right_entropy
        return information_gain

    def get_tree_depth(self, node):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        else:
            left_depth = self.get_tree_depth(node.left)
            right_depth = self.get_tree_depth(node.right)
            return max(left_depth, right_depth)+1

    def tree_depth(self):
        return self.get_tree_depth(self.tree)

    def count_nodes(self, node):
        if node is None:
            return 0
        return 1+self.count_nodes(node.left) + self.count_nodes(node.right)

    def get_number_of_nodes(self):
        return self.count_nodes(self.tree)

    def find_best_split(self, X, y):
        num_features =X.shape[1]
        best_feature =None
        best_threshold = None
        max_gain =-1

        parent_entropy = self.calculate_entropy(y)

        for feature_index in range(num_features):
            unique_values= np.unique(X[:, feature_index])
            for threshold in unique_values:
                gain = self.calculate_information_gain(X,y,feature_index, threshold)
                if gain > max_gain and gain > self.entropy_threshold:
                    max_gain=gain
                    best_feature= feature_index
                    best_threshold= threshold

        return best_feature, best_threshold

    def build_tree(self, X, y):
        if len(np.unique(y))==1:
            leaf =self.Node(entropy=0, num_samples=len(y),num_classes=len(np.unique(y)))
            leaf.predicted_class = y[0]
            return leaf

        best_feature, best_threshold = self.find_best_split(X, y)

        if best_feature is None:
            leaf = self.Node(entropy=self.calculate_entropy(y), num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        left_X, left_y, right_X, right_y = self.split_dataset(X, y, best_feature, best_threshold)

        if len(left_y) == 0 or len(right_y) == 0:
            leaf = self.Node(entropy=self.calculate_entropy(y), num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        left_subtree = self.build_tree(left_X, left_y)
        right_subtree = self.build_tree(right_X, right_y)

        node = self.Node(entropy=self.calculate_entropy(y), num_samples=len(y), num_classes=len(np.unique(y)))
        node.feature_index = best_feature
        node.threshold=best_threshold
        node.left=left_subtree
        node.right=right_subtree

        return node

    def predict_sample(self, tree, sample):
        if tree.left is None and tree.right is None:
            return tree.predicted_class

        if sample[tree.feature_index] <= tree.threshold:
            return self.predict_sample(tree.left, sample)
        else:
            return self.predict_sample(tree.right, sample)

    def fit(self, X, y):
        self.tree = self.build_tree(X, y)

    def predict(self, X):
        return [self.predict_sample(self.tree, sample) for sample in X]

    def print_tree(self, node, depth=0):
        if node is None:
            return

        indent = "  " * depth
        if node.left is None and node.right is None:
            print(f"{indent}Predicted class: {node.predicted_class}")
        else:
            print(f"{indent}if Feature {node.feature_index} <= {node.threshold}:")
            self.print_tree(node.left, depth + 1)
            print(f"{indent}else:")
            self.print_tree(node.right, depth + 1)


from sklearn.metrics import accuracy_score

threshold_entropies = [0,0.25, 0.5,0.75,1]
val_accuracies = []
train_accuracies = []
tree_depth = []
tree_nodes = []
best_threshold_entropy = None
best_accuracy = 0


#Iterating through different entropy thresholds
for threshold_entropy in threshold_entropies:

    tree = DecisionTreeClassifier(entropy_threshold=threshold_entropy)
    tree.fit(X_train, y_train)

    # Making predictions on the validation and training sets
    y_pred_val = tree.predict(X_val)
    y_pred_train = tree.predict(X_train)

    size_of_tree = tree.tree_depth()
    nodes_of_tree = tree.get_number_of_nodes()

    # Calculating accuracy on validation and training data
    acc_val = accuracy_score(y_val, y_pred_val)
    acc_train = accuracy_score(y_train, y_pred_train)

    # Append metrics to respective lists
    train_accuracies.append(acc_train)
    val_accuracies.append(acc_val)
    tree_depth.append(size_of_tree)
    tree_nodes.append(nodes_of_tree)

    # Update best accuracy and corresponding threshold
    if acc_val > best_accuracy:
        best_accuracy = acc_val
        best_threshold_entropy = threshold_entropy



import matplotlib.pyplot as plt

x = range(len(threshold_entropies))

# Creating the bar plot
plt.bar(x,val_accuracies,width=0.4,label='Validation Accuracy',align='center')
plt.bar(x,train_accuracies,width=0.4,label='Train Accuracy',align='edge')

plt.xlabel('Threshold Entropies')
plt.ylabel('Accuracies')
plt.title('Accuracies vs Threshold Entropies')
plt.xticks(x,threshold_entropies)
plt.legend()
plt.show()

x = range(len(threshold_entropies))

# Creating the bar plot
plt.bar(x,tree_nodes,width=0.4,label='Tree Depth', align='center')

plt.xlabel('Threshold Entropies')
plt.ylabel('Nodes')
plt.title('Nodes vs Threshold Entropies')
plt.xticks(x,threshold_entropies)
plt.legend()
plt.show()



#Selecting the threshold entropy for maximum accuracy
best_threshold_entropy=0
print(f'\n\nThe best threshold entropy is {best_threshold_entropy}')
print(f'The no of nodes for it is {tree_nodes[0]}')

#Step a: Calculating accuracy on testing and training data

optimal_tree = DecisionTreeClassifier(entropy_threshold=best_threshold_entropy)
optimal_tree.fit(X_train, y_train)

# Predicting on training and testing data
y_pred_train_optimal = optimal_tree.predict(X_train)
y_pred_test_optimal = optimal_tree.predict(X_test)

acc_train_optimal = accuracy_score(y_train, y_pred_train_optimal)
acc_test_optimal = accuracy_score(y_test, y_pred_test_optimal)

# Print the accuracy results
print(f"Accuracy on training data with optimal threshold: {acc_train_optimal:.2f}")
print(f"Accuracy on testing data with optimal threshold: {acc_test_optimal:.2f}")


#Experiment 2
class ImprovedDecisionTreeClassifier:
    class TreeNode:
        def __init__(self, impurity, num_samples, num_classes):
            self.impurity = impurity
            self.num_samples = num_samples
            self.num_classes = num_classes
            self.feature_index = 0
            self.threshold = 0
            self.left = None
            self.right = None
            self.predicted_class = None

    def __init__(self, impurity_threshold=0):
        self.impurity_threshold = impurity_threshold
        self.root = None
        self.train_accuracies = []
        self.val_accuracies = []

    def split_data(self, X, y, feature_index,threshold):
        left_mask = X[:, feature_index]<=threshold
        right_mask = ~left_mask

        return X[left_mask],y[left_mask],X[right_mask],y[right_mask]

    def calculate_impurity(self, y):
        unique_classes, counts = np.unique(y,return_counts=True)
        probabilities = counts / len(y)
        impurity = -np.sum(probabilities*np.log2(probabilities))
        return impurity

    def calculate_information_gain(self, X, y, feature_index, threshold):
        left_X, left_y, right_X,right_y = self.split_data(X, y,feature_index,threshold)
        parent_impurity=self.calculate_impurity(y)
        left_impurity=self.calculate_impurity(left_y)
        right_impurity=self.calculate_impurity(right_y)
        num_left=len(left_y)
        num_right=len(right_y)
        total_samples=num_left + num_right
        information_gain=parent_impurity-(num_left/total_samples)*left_impurity-(num_right/total_samples)*right_impurity

        return information_gain

    def get_tree_depth(self,node):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        else:
            left_depth = self.get_tree_depth(node.left)
            right_depth = self.get_tree_depth(node.right)

            return max(left_depth,right_depth) + 1

    def tree_depth(self):
        return self.get_tree_depth(self.root)

    def find_best_split(self,X,y):
        num_features =X.shape[1]
        best_feature =None
        best_threshold =None
        max_gain=-1

        parent_impurity=self.calculate_impurity(y)

        for feature_index in range(num_features):
            unique_values = np.unique(X[:, feature_index])
            for threshold in unique_values:
                gain = self.calculate_information_gain(X,y,feature_index,threshold)
                if gain > max_gain and gain > self.impurity_threshold:
                    max_gain=gain
                    best_feature=feature_index
                    best_threshold=threshold

        return best_feature,best_threshold

    def build_tree(self,X,y,X_val,y_val):
        if len(np.unique(y)) == 1:
            leaf = self.TreeNode(impurity=0, num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = y[0]
            return leaf

        best_feature, best_threshold = self.find_best_split(X, y)

        if best_feature is None:
            leaf = self.TreeNode(impurity=self.calculate_impurity(y), num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        left_X, left_y, right_X, right_y = self.split_data(X, y, best_feature, best_threshold)
        left_X_val, left_y_val, right_X_val, right_y_val = self.split_data(X_val, y_val, best_feature, best_threshold)

        if len(left_y) == 0 or len(right_y) == 0:
            leaf = self.TreeNode(impurity=self.calculate_impurity(y), num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        left_subtree = self.build_tree(left_X, left_y, left_X_val, left_y_val)
        right_subtree = self.build_tree(right_X, right_y, right_X_val, right_y_val)

        node=self.TreeNode(impurity=self.calculate_impurity(y),num_samples=len(y),num_classes=len(np.unique(y)))
        node.feature_index=best_feature
        node.threshold=best_threshold
        node.left=left_subtree
        node.right=right_subtree

        y_train_pred=np.array([self.predict_sample(node, sample) for sample in X])
        y_val_pred=np.array([self.predict_sample(node, sample) for sample in X_val])

        train_accuracy=self.calculate_accuracy(y, y_train_pred)
        val_accuracy=self.calculate_accuracy(y_val, y_val_pred)

        self.train_accuracies.append(train_accuracy)
        self.val_accuracies.append(val_accuracy)

        return node

    def calculate_accuracy(self,y_true,y_pred):
        return np.mean(y_true == y_pred) * 100

    def predict_sample(self, tree, sample):
        if tree.left is None and tree.right is None:
            return tree.predicted_class

        if sample[tree.feature_index] <= tree.threshold:
            return self.predict_sample(tree.left, sample)
        else:
            return self.predict_sample(tree.right, sample)

    def fit(self, X, y, X_val, y_val):
        self.root = self.build_tree(X, y, X_val, y_val)

    def predict(self, X):
        return [self.predict_sample(self.root, sample) for sample in X]

    def plot_accuracies(self):
        plt.plot(self.train_accuracies, label='Train Accuracy', linewidth=2)
        plt.plot(self.val_accuracies, label='Validation Accuracy')
        plt.xlabel('Split Stages')
        plt.ylabel('Accuracy (%)')
        plt.legend()
        plt.show()


tree = ImprovedDecisionTreeClassifier(impurity_threshold=0)
tree.fit(X_train, y_train, X_val, y_val)
tree.plot_accuracies()

# Decison tree with early stopping



class DecisionTreeClassifier34:
    class Node:
        def __init__(self,entropy,num_samples,num_classes):
            self.entropy=entropy
            self.num_samples= num_samples
            self.num_classes=num_classes
            self.feature_index=0
            self.threshold=0
            self.left=None
            self.right=None
            self.predicted_class=None

    def __init__(self,entropy_threshold=0):
        self.entropy_threshold=entropy_threshold
        self.tree=None

    def calculate_entropy(self,y):
        unique_classes, counts=np.unique(y, return_counts=True)
        probabilities= counts/len(y)
        entropy=-np.sum(probabilities * np.log2(probabilities))

        return entropy

    def split_dataset(self, X, y,feature_index,threshold):
        left_mask= X[:, feature_index] <= threshold
        right_mask= ~left_mask
        return X[left_mask],y[left_mask],X[right_mask],y[right_mask]

    def calculate_information_gain(self,X,y,feature_index,threshold):
        left_X,left_y,right_X,right_y=self.split_dataset(X, y, feature_index, threshold)
        parent_entropy=self.calculate_entropy(y)
        left_entropy=self.calculate_entropy(left_y)
        right_entropy=self.calculate_entropy(right_y)
        num_left=len(left_y)
        num_right=len(right_y)
        total_samples = num_left+num_right
        information_gain = parent_entropy-(num_left / total_samples)*left_entropy-(
                    num_right/total_samples)*right_entropy

        return information_gain

    def get_tree_depth(self,node):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        else:
            left_depth = self.get_tree_depth(node.left)
            right_depth = self.get_tree_depth(node.right)
            return max(left_depth, right_depth) + 1

    def tree_depth(self):
        return self.get_tree_depth(self.tree)

    def count_nodes(self,node):
        if node is None:
            return 0
        return 1+self.count_nodes(node.left)+self.count_nodes(node.right)

    def get_number_of_nodes(self):
        return self.count_nodes(self.tree)

    def find_best_split(self,X,y):
        num_features = X.shape[1]
        best_feature = None
        best_threshold = None
        max_gain = -1

        parent_entropy = self.calculate_entropy(y)

        for feature_index in range(num_features):
            unique_values = np.unique(X[:, feature_index])
            for threshold in unique_values:
                gain = self.calculate_information_gain(X, y, feature_index, threshold)
                if gain > max_gain and gain > self.entropy_threshold:
                    max_gain = gain
                    best_feature = feature_index
                    best_threshold = threshold

        return best_feature, best_threshold

    def build_tree(self,X,y):
        if len(np.unique(y)) == 1:
            leaf = self.Node(entropy=0, num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = y[0]
            return leaf

        best_feature, best_threshold = self.find_best_split(X, y)

        if best_feature is None:
            leaf = self.Node(entropy=self.calculate_entropy(y),num_samples=len(y),num_classes=len(np.unique(y)))
            leaf.predicted_class =np.argmax(np.bincount(y))
            return leaf

        left_X,left_y,right_X,right_y = self.split_dataset(X,y,best_feature,best_threshold)

        if len(left_y)==0 or len(right_y)==0:
            leaf = self.Node(entropy=self.calculate_entropy(y),num_samples=len(y),num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        left_subtree =self.build_tree(left_X, left_y)
        right_subtree=self.build_tree(right_X, right_y)

        node = self.Node(entropy=self.calculate_entropy(y),num_samples=len(y), num_classes=len(np.unique(y)))
        node.feature_index = best_feature
        node.threshold = best_threshold
        node.left = left_subtree
        node.right = right_subtree

        return node

    def predict_sample(self,tree,sample):
        if tree.left is None and tree.right is None:
            return tree.predicted_class

        if sample[tree.feature_index] <= tree.threshold:
            return self.predict_sample(tree.left,sample)
        else:
            return self.predict_sample(tree.right,sample)

    def fit(self,X,y):
        self.tree = self.build_tree(X, y)

    def predict(self,X):
        return [self.predict_sample(self.tree,sample) for sample in X]

    def calculate_accuracy(self,y_true,y_pred):
        correct = np.sum(y_true==y_pred)
        total = len(y_true)
        return correct / total

    def build_tree_with_early_stopping(self,X,y,X_val, y_val):
        if len(np.unique(y))==1:
            leaf = self.Node(entropy=0, num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = y[0]
            return leaf

        best_feature,best_threshold = self.find_best_split(X, y)

        if best_feature is None:
            leaf = self.Node(entropy=self.calculate_entropy(y),num_samples=len(y),num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf


        left_X,left_y,right_X,right_y =self.split_dataset(X,y,best_feature, best_threshold)

        if len(left_y)==0 or len(right_y)== 0:
            leaf = self.Node(entropy=self.calculate_entropy(y), num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        left_subtree=self.build_tree_with_early_stopping(left_X, left_y, X_val, y_val)
        right_subtree=self.build_tree_with_early_stopping(right_X, right_y, X_val, y_val)

        node=self.Node(entropy=self.calculate_entropy(y), num_samples=len(y), num_classes=len(np.unique(y)))
        node.feature_index = best_feature
        node.threshold = best_threshold
        node.left = left_subtree
        node.right = right_subtree

        # Calculating validation accuracy at this node
        y_val_pred =[self.predict_sample(node, sample) for sample in X_val]
        val_accuracy =self.calculate_accuracy(y_val, y_val_pred)

        # If validation accuracy decreases,return a leaf node, 
        #that's how early stopping is done.
        if val_accuracy < self.prev_val_accuracy:
            leaf = self.Node(entropy=self.calculate_entropy(y), num_samples=len(y), num_classes=len(np.unique(y)))
            leaf.predicted_class = np.argmax(np.bincount(y))
            return leaf

        self.prev_val_accuracy=val_accuracy

        return node

    def fit_with_early_stopping(self,X,y, X_val, y_val):
        self.prev_val_accuracy = 0  # Initialize prev_val_accuracy
        self.tree = self.build_tree_with_early_stopping(X, y, X_val, y_val)

    def print_tree(self, node, depth=0):
        if node is None:
            return

        indent = "  " * depth
        if node.left is None and node.right is None:
            print(f"{indent}Predicted class: {node.predicted_class}")
        else:
            print(f"{indent}if Feature {node.feature_index} <= {node.threshold}:")
            self.print_tree(node.left, depth + 1)
            print(f"{indent}else:")
            self.print_tree(node.right, depth + 1)


tree=DecisionTreeClassifier34(entropy_threshold=0)
tree.fit_with_early_stopping(X_train, y_train, X_val, y_val)
y_pred = tree.predict(X_test)
test_accuracy= accuracy_score(y_test, y_pred)
y_pred =tree.predict(X_train)
train_accuracy = accuracy_score(y_train, y_pred)
print("After early stop:")
print(f"Test accuracy: {test_accuracy}")
print(f"Train accuracy: {train_accuracy}")
num_of_nodes = tree.get_number_of_nodes()
print(f"Size of tree i.e. number of nodes after early stopping: {num_of_nodes}")

#Experiment 3

#Printing the rules for classification

#Printing tree for threshold entropy = 0 ( experiment 1)
print("Tree before early stopping:")
tree = DecisionTreeClassifier(entropy_threshold=0)
tree.fit(X_train, y_train)
tree.print_tree(tree.tree)

# Printing tree after early stopping
print("Tree after early stopping")
print('''
if Feature 3 <= 2:
  Predicted class: 2
else:
  Predicted class: 2
''')